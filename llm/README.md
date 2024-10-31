# LLM部分

## 进度

模型使用HuatuoGPT2-7B

已在本地完成部署，成功进行本地推理（CLI）

已封装接口，成功进行多轮对话，可以连接 server


## 使用

下载模型并放在`./HuatuoGPT2_7B/`

```
conda create -n <name> python=3.12

conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

conda install transformers

conda install sentencepiece
```

## 致谢

* 【HuatuoGPT】 https://github.com/FreedomIntelligence/HuatuoGPT

* 【HuatuoGPT2】 https://github.com/FreedomIntelligence/HuatuoGPT-II