import argparse
import logging
import warnings

from llm.engine_v1 import LlmEngine


class HealthAssistantServer:
    def __init__(self):
        logging.info('Starting HealthAssistantServer...')
        warnings.filterwarnings('ignore', category=FutureWarning)

        parser = argparse.ArgumentParser()
        parser.add_argument("--model-name", type=str, default="./HuatuoGPT2_7B/")
        parser.add_argument("--device", type=str, choices=["cuda", "cpu"], default="cuda")
        parser.add_argument("--num-gpus", type=str, default="1")
        # parser.add_argument("--load-8bit", action="store_true")
        parser.add_argument("--temperature", type=float, default=0.5)
        parser.add_argument("--max-new-tokens", type=int, default=512)
        args = parser.parse_args()

        self.engine = LlmEngine(args)

        logging.info('Starting getting engine history...')

        self.history = self.engine.history

    def generate(self, query: str, query_id: int = 0) -> str:
        """
        :param query: 问题
        :param query_id: 会话id，留空的时候就一直使用同一个
        :return: 回答
        """
        return self.engine.generate(query, query_id)

    def start_new_conversation(self) -> int:
        # 返回一个新的 query_id
        return len(self.history)

    def stop(self):
        self.engine.stop()
        del self.history
        del self.engine


def init_logging():
    logger = logging.getLogger()

    fh = logging.FileHandler('logger.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[%(lineno)d]: %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)

    logger.info('Finish init_logging')
