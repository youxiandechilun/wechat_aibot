import tkinter as tk
from tkinter import ttk
from config.config_manager import ConfigManager


class RulesTab:
    def __init__(self, parent, config):
        self.config = config
        self.frame = ttk.Frame(parent, padding=10)

        # 初始化变量
        self.reply_when_mentioned = tk.BooleanVar(value=config.get("reply_when_mentioned", True))
        self.auto_reply_all = tk.BooleanVar(value=config.get("auto_reply_all", False))
        self.debug_mode = tk.BooleanVar(value=config.get("debug_mode", True))

        self.setup_ui()

    def setup_ui(self):
        # 回复规则设置框架
        rules_frame = ttk.LabelFrame(self.frame, text="回复规则设置", padding=10)
        rules_frame.pack(fill=tk.X, pady=5)

        # 规则选项
        ttk.Checkbutton(rules_frame,
                        text="群聊中仅回复@我的消息",
                        variable=self.reply_when_mentioned).pack(anchor=tk.W, pady=5)

        ttk.Checkbutton(rules_frame,
                        text="自动回复所有好友消息",
                        variable=self.auto_reply_all).pack(anchor=tk.W, pady=5)

        ttk.Checkbutton(rules_frame,
                        text="启用调试模式",
                        variable=self.debug_mode).pack(anchor=tk.W, pady=5)

    def save_config(self):
        self.config.set("reply_when_mentioned", self.reply_when_mentioned.get())
        self.config.set("auto_reply_all", self.auto_reply_all.get())
        self.config.set("debug_mode", self.debug_mode.get())

    def load_config(self):
        self.reply_when_mentioned.set(self.config.get("reply_when_mentioned", True))
        self.auto_reply_all.set(self.config.get("auto_reply_all", False))
        self.debug_mode.set(self.config.get("debug_mode", True))