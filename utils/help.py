"""
wechat_ai_bot/utils/help.py

微信AI助手帮助文档模块
"""

HELP_CONTENT = """
🤖 微信AI智能助手使用指南

1. AI设置
  - 选择AI引擎：Ollama(本地)或DeepSeek(在线)
  - Ollama：需要本地运行Ollama服务
  - DeepSeek：需要有效的API密钥

2. 微信设置
  - 自动回复的好友：设置要自动回复的好友昵称，多个用逗号分隔
  - 自动回复的群聊：刷新群列表并选择要监控的群聊

3. 回复规则
  - 群聊中仅回复@我的消息：避免回复群聊中所有消息
  - 自动回复所有好友消息：启用后将回复所有好友消息
  - 调试模式：显示详细日志

4. 使用步骤
  - 配置AI引擎和微信设置
  - 点击"刷新群列表"加载群聊
  - 添加要自动回复的群聊
  - 点击"启动助手"开始监控
  - 确保微信窗口处于打开状态

5. 注意事项
  - 程序运行时不要关闭微信
  - 定期保存配置
  - 群聊监控需要保持群聊窗口打开
  - 请勿用于商业用途或违反微信用户协议的行为

6. 常见问题
  Q: 为什么收不到自动回复？
  A: 请检查：1) 微信窗口是否打开 2) 是否在自动回复列表中 3) 群聊中是否开启了"仅回复@我的消息"

  Q: 如何测试AI连接？
  A: 在AI设置标签页点击对应引擎的"测试连接"按钮

  Q: 为什么日志显示"忽略消息"？
  A: 这可能是因为：1) 消息不符合回复规则 2) 发送者是系统账号 3) 调试模式未开启

版本信息: v1.0.0
最后更新: 2023-12-01
"""


class HelpSystem:
    @staticmethod
    def show_help(parent=None):
        """显示帮助信息"""
        import tkinter as tk
        from tkinter import ttk

        help_window = tk.Toplevel(parent)
        help_window.title("微信AI助手帮助文档")
        help_window.geometry("800x600")

        # 主框架
        main_frame = ttk.Frame(help_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标签页
        tab_control = ttk.Notebook(main_frame)

        # 使用指南标签页
        guide_tab = ttk.Frame(tab_control, padding=10)
        tab_control.add(guide_tab, text="使用指南")

        # 常见问题标签页
        faq_tab = ttk.Frame(tab_control, padding=10)
        tab_control.add(faq_tab, text="常见问题")

        tab_control.pack(fill=tk.BOTH, expand=True)

        # 使用指南内容
        guide_text = tk.Text(guide_tab, wrap=tk.WORD, padx=10, pady=10)
        guide_text.pack(fill=tk.BOTH, expand=True)
        guide_text.insert(tk.END, HELP_CONTENT.split("6. 常见问题")[0])
        guide_text.config(state=tk.DISABLED)

        # 常见问题内容
        faq_text = tk.Text(faq_tab, wrap=tk.WORD, padx=10, pady=10)
        faq_text.pack(fill=tk.BOTH, expand=True)
        faq_part = "6. 常见问题" + HELP_CONTENT.split("6. 常见问题")[1]
        faq_text.insert(tk.END, faq_part)
        faq_text.config(state=tk.DISABLED)

        # 关闭按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="关闭", command=help_window.destroy).pack(side=tk.RIGHT)

    @staticmethod
    def get_help_text():
        """获取纯文本帮助内容"""
        return HELP_CONTENT

    @staticmethod
    def show_quick_help(parent=None):
        """显示简版帮助信息"""
        import tkinter as tk
        from tkinter import messagebox
        quick_help = "微信AI助手快速指南\n\n" + HELP_CONTENT.split("5. 注意事项")[0]
        messagebox.showinfo("快速帮助", quick_help, parent=parent)