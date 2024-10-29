import logging

from llm.server_v1 import HealthAssistantServer

if __name__ == '__main__':

    logging.basicConfig(filename='logger.log', level=logging.INFO)

    # step 1：初始化LLM
    server = HealthAssistantServer()

    print("HuatuoGPT: 你好，我是一个解答医疗健康问题的大模型，目前处于测试阶段，请以医嘱为准。请问有什么可以帮到您？")

    # step 2：开始对话
    while True:
        query = input("\n用户：")

        # 调用 server.generate()，传入问题，返回答案
        # 可能要等很久。。。
        answer = server.generate(query)
        print(answer)
