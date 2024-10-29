import logging
import platform
import torch
from queue import Queue
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM


class LlmEngine:
    def __init__(self, args):

        logging.info('Starting LlmEngine...')

        self.args = args

        if args.device == "cuda":
            kwargs = {"torch_dtype": torch.float32}
            if args.num_gpus == "auto":
                kwargs["device_map"] = "auto"
            else:
                num_gpus = int(args.num_gpus)
                if num_gpus != 1:
                    kwargs.update({
                        "device_map": "auto",
                        "max_memory": {i: "13GiB" for i in range(num_gpus)},
                    })
        elif args.device == "cpu":
            kwargs = {}
        else:
            raise ValueError(f"Invalid device: {args.device}")

        logging.info('Initializing tokenizer and model...')

        self.tokenizer = AutoTokenizer.from_pretrained(
            args.model_name,
            padding_side="right",
            use_fast=True,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(args.model_name, trust_remote_code=True, **kwargs)
        if args.device == "cuda" and args.num_gpus == 1:
            self.model.cuda()

        self.model = self.model.eval()

        logging.info('Finished initializing tokenizer and model.')

        self.os_name = platform.system()
        self.clear_command = 'cls' if self.os_name == 'Windows' else 'clear'
        self.history: dict = {}
        # self.taskQueue = Queue()
        # self.resultQueue = Queue()
        #
        # logging.info('Start new Thread...')
        #
        # self.process = threading.Thread(target=self.listen, args=[self.taskQueue, self.resultQueue])
        # self.process.start()

    def listen(self, task_queue: Queue, result_queue: Queue):

        logging.info('Start listening...')

        while True:
            query, history = task_queue.get(block=True, timeout=None)

            logging.info(f'Received query {query}')

            gen_tokens_cnt = 0
            result = ""
            outputs = ""
            for outputs in self.forward_stream(
                    query,
                    history,
                    max_new_tokens=self.args.max_new_tokens,
                    temperature=self.args.temperature,
                    repetition_penalty=1.2,
                    context_len=1024
            ):
                outputs = outputs.strip()

                logging.info('Generated tokens: %s', outputs)

                new_token_len = len(outputs)
                if new_token_len - 1 > gen_tokens_cnt:
                    result += outputs[gen_tokens_cnt:new_token_len - 1] + "\n"
                    gen_tokens_cnt = new_token_len - 1
            result += outputs[gen_tokens_cnt:]

            logging.info('Output: %s', result)

            result_queue.put(result)

    def generate(self, query: str, query_id: int = 0) -> str:
        if query_id not in self.history:
            self.history[query_id] = []
        if query == "clear":
            self.history[query_id] = []
            return ""
        history = self.history[query_id]

        # logging.info('Put new task into queue...')
        #
        # self.taskQueue.put((query, history), block=True, timeout=None)
        # result = self.resultQueue.get(block=True, timeout=None)
        # self.history[query_id] = history + [(query, result)]
        #
        # logging.info('Get result from queue...')

        logging.info(f'Received query {query}')

        gen_tokens_cnt = 0
        result = ""
        outputs = ""
        for outputs in self.forward_stream(
                query,
                history,
                max_new_tokens=self.args.max_new_tokens,
                temperature=self.args.temperature,
                repetition_penalty=1.2,
                context_len=1024
        ):
            outputs = outputs.strip()

            logging.info('Generated tokens: %s', outputs)

            new_token_len = len(outputs)
            if new_token_len - 1 > gen_tokens_cnt:
                result += outputs[gen_tokens_cnt:new_token_len - 1] + "\n"
                gen_tokens_cnt = new_token_len - 1
        result += outputs[gen_tokens_cnt:]

        logging.info('Output: %s', result)

        return result

    @torch.inference_mode()
    def forward_stream(
            self,
            query,
            history,
            max_new_tokens=512,
            temperature=0.2,
            repetition_penalty=1.2,
            context_len=1024,
            stream_interval=2
    ):
        def load_history(_query, _history, eos):
            if not _history:
                return f"""一位用户和智能医疗大模型HuatuoGPT之间的对话。对于用户的医疗问诊，HuatuoGPT给出准确的、详细的、温暖的指导建议。
                对于用户的指令问题，HuatuoGPT给出有益的、详细的、有礼貌的回答。<病人>：{_query} <HuatuoGPT>："""
            else:
                _prompt = (
                    '一位用户和智能医疗大模型HuatuoGPT之间的对话。对于用户的医疗问诊，HuatuoGPT给出准确的、详细的、温暖的指导建议。'
                    '对于用户的指令问题，HuatuoGPT给出有益的、详细的、有礼貌的回答。'
                )
                for index, (old_query, response) in enumerate(_history):
                    _prompt += "<病人>：{} <HuatuoGPT>：{}".format(old_query, response) + eos
                _prompt += "<病人>：{} <HuatuoGPT>：".format(_query)
                return _prompt

        prompt = load_history(query, history, self.tokenizer.eos_token)
        input_ids = self.tokenizer(prompt).input_ids
        output_ids = list(input_ids)

        device = self.model.device
        stop_str = self.tokenizer.eos_token
        stop_token_ids = [self.tokenizer.eos_token_id]

        prompt_len = len(self.tokenizer.decode(input_ids, skip_special_tokens=False))

        max_src_len = context_len - max_new_tokens - 8
        input_ids = input_ids[-max_src_len:]

        token = None
        past_key_values = None

        for i in range(max_new_tokens):
            if i == 0:
                out = self.model(torch.as_tensor([input_ids], device=device), use_cache=True)
                logits = out.logits
                past_key_values = out.past_key_values
            else:
                out = self.model(
                    input_ids=torch.as_tensor([[token]], device=device),
                    use_cache=True,
                    past_key_values=past_key_values,
                )
                logits = out.logits
                past_key_values = out.past_key_values

            last_token_logits = logits[0][-1]

            if device == "mps":
                # Switch to CPU by avoiding some bugs in mps backend.
                last_token_logits = last_token_logits.float().to("cpu")

            if temperature < 1e-4:
                token = int(torch.argmax(last_token_logits))
            else:
                probs = torch.softmax(last_token_logits / temperature, dim=-1)
                token = int(torch.multinomial(probs, num_samples=1))

            output_ids.append(token)

            if token in stop_token_ids:
                stopped = True
            else:
                stopped = False

            if i % stream_interval == 0 or i == max_new_tokens - 1 or stopped:
                output = self.tokenizer.decode(output_ids, skip_special_tokens=False)
                if stop_str:
                    pos = output.rfind(stop_str, prompt_len)
                    if pos != -1:
                        output = output[prompt_len:pos]
                        stopped = True
                    else:
                        output = output[prompt_len:]
                    yield output
                else:
                    raise NotImplementedError

            if stopped:
                break

        del past_key_values

    def stop(self):
        del self.model
        del self.tokenizer
