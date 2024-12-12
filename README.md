# HealthAssistantClone
人工智能原理应用第三组

## 使用

* 下载模型并放在`./HuatuoGPT2_7B/`

* 创建环境

  ```bash
  conda create -n <name> python=3.12
  conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
  conda install Flask flask-cors transformers sentencepiece
  ```

* 启动服务器

  ```bash
  python app.py
  ```

* 使用

  使用浏览器打开`用户页面.html`，进行对话。

## 致谢

* 模型使用`HuatuoGPT2-7B`

* 部分代码参考了以下项目：

  > 【HuatuoGPT】 https://github.com/FreedomIntelligence/HuatuoGPT
  >
  > 【HuatuoGPT2】 https://github.com/FreedomIntelligence/HuatuoGPT-II 

