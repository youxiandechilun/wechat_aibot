# 微信AI智能助手

## 项目概述

这是一个基于 `wxauto`、`PyQt5` 和 AI 大模型（DeepSeek/Ollama）的微信智能聊天助手系统，旨在实现自动化的消息处理和智能回复功能。

## 核心功能

### 智能对话服务

*   支持私聊和群聊场景的自动回复。
*   提供可配置的触发条件和回复规则。
*   具备多轮对话上下文保持能力。

### 多模型支持

*   集成云端 DeepSeek 大模型。
*   支持本地 Ollama 开源模型。
*   采用统一的 AI 引擎接口设计，便于扩展。

### 可视化管理系统

*   提供直观的 PyQt5 图形化控制界面。
*   支持实时对话监控和日志查看。
*   允许灵活的角色设定和系统配置。

## 项目结构

```
wechat_ai_bot/
├── main.py                 # 系统入口
├── config/                 # 配置管理模块
│   ├── config_manager.py   # 配置加载与保存
│   └── constants.py        # 系统常量定义
├── core/                   # 核心逻辑模块
│   ├── ai_engine.py        # AI 引擎抽象接口
│   ├── deepseek_client.py  # DeepSeek AI 客户端
│   ├── ollama_client.py    # Ollama AI 客户端
│   └── message_processor.py # 微信消息处理逻辑
├── service/                # 微信服务模块
│   ├── wechat_service.py   # 微信接口封装
│   └── message_monitor.py  # 微信消息监听与分发
├── ui/                     # 用户界面模块
│   ├── main_window.py      # 主窗口界面
│   └── tabs/               # 各功能选项卡
└── utils/                  # 工具函数模块
    ├── help.py             # 帮助文档与实用函数
    └── logger.py           # 日志记录系统
```

## 安装指南

1.  **获取项目代码**

    ```bash
    git clone https://github.com/YourGitHubUsername/wechat_ai_bot.git
    cd wechat_ai_bot
    ```

2.  **安装依赖环境**

    ```bash
    pip install -r requirements.txt
    ```

3.  **配置参数**

    创建或修改 `wechat_ai_config.json` 文件，根据您的需求配置 AI 引擎、API 密钥和角色设定等：

    ```json
    {
      "ai_engine": "deepseek",
      "ollama_host": "http://localhost:11434",
      "ollama_model": "deepseek-r1:8b",
      "deepseek_api_key": "您的API密钥",
      "ai_persona": "智能助手",
      "persona_desc": "我是一个友好且专业的AI助手",
      "auto_reply_friends": "",
      "reply_when_mentioned": true,
      "auto_reply_all": false,
      "debug_mode": true
    }
    ```

## 使用说明

1.  **准备工作**

    *   请确保您的 PC 端微信已登录（测试版本为 `3.9.15.51`）。
    *   请将微信发送消息的快捷键设置为"回车键"。
    *   **重要提示：** 启动系统后，请保持目标聊天窗口为当前活动窗口，否则可能出现回复错位。

2.  **启动系统**

    ```bash
    python main.py
    ```

## 注意事项与已知问题

### 功能限制

*   当前仅支持单窗口焦点模式下的消息回复。
*   群聊 `@` 识别功能存在部分限制，可能出现非 `@` 消息也被回复的情况。
*   群聊昵称无法被获取，打开群聊窗口便可以回复，但是可能出现非 `@` 消息也被回复的情况。

### 使用建议

*   建议您在正式使用前，先在测试账号上进行功能验证，以熟悉系统行为。
*   群聊功能需谨慎使用，以避免不必要的干扰或潜在的平台限制（请参考微信平台相关规定）。非常容易封禁一天时间
*   请合理控制自动回复的频率，避免高频次的回复行为。

## 参与贡献

我们欢迎您通过 Issue 提交问题反馈或通过 Pull Request 贡献代码。在贡献之前，建议您：

*   详细描述问题现象或改进方案。
*   提供可复现的测试用例。
*   确保您的代码符合项目规范。

--- 

**提示：** 本项目主要用于技术研究与交流，请务必遵守微信平台使用规范，并合理控制自动回复频率。