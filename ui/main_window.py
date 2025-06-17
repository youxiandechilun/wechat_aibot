import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
from config.config_manager import ConfigManager
from .tabs.ai_tab import AITab
from .tabs.wechat_tab import WechatTab
from .tabs.rules_tab import RulesTab
from service.wechat_service import WeChatService


class MainWindow:
    def __init__(self, config, wechat_service, monitor, bot_nickname):
        self.root = tk.Tk()
        self.root.title("🤖 微信AI智能助手")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 设置应用图标 (从root.py迁移)
        try:
            self.root.iconbitmap("ai_icon.ico")
        except:
            pass

        self.config = config
        self.wechat_service = wechat_service
        self.monitor = monitor
        self.bot_nickname = bot_nickname # Store bot nickname

        # 初始化主窗口相关变量 (从root.py迁移)
        self.is_running = False
        self.last_log_message = ""
        self.monitor_thread = None
        self.log_text = None  # 在setup_ui中创建
        self.status_var = tk.StringVar(value="就绪") # 在setup_ui中创建
        self.auto_reply_friends = tk.StringVar() # 初始化auto_reply_friends

        self.setup_ui()
        self.load_config() # 现在会调用ConfigManager的load_config和各tab的load_config

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建标签页
        tab_control = ttk.Notebook(main_frame)

        # 添加各个标签页
        self.ai_tab = AITab(tab_control, self.config, self.log_message)
        self.wechat_tab = WechatTab(tab_control, self.log_message, self.wechat_service, self.auto_reply_friends)
        self.rules_tab = RulesTab(tab_control, self.config)

        tab_control.add(self.ai_tab.frame, text="AI设置")
        tab_control.add(self.wechat_tab, text="微信设置")
        tab_control.add(self.rules_tab.frame, text="回复规则")

        tab_control.pack(fill=tk.BOTH, expand=True)

        # --- 控制按钮区域 (从root.py迁移) ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(control_frame, text="▶ 启动助手", command=self.start_bot, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = ttk.Button(control_frame, text="■ 停止助手", command=self.stop_bot, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        ttk.Button(control_frame, text="🗑️ 清除日志", command=self.clear_logs).pack(side=tk.LEFT, padx=10)

        ttk.Button(control_frame, text="💾 保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=10)
        ttk.Button(control_frame, text="❓ 帮助", command=self.show_help).pack(side=tk.RIGHT, padx=10)

        # --- 日志区域 (从root.py迁移) ---
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 日志颜色配置
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("DEBUG", foreground="gray")
        self.log_text.config(state=tk.DISABLED)

        # --- 状态栏 (从root.py迁移) ---
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log_message(self, message, level="INFO"):
        # 如果与上一条日志相同，则不重复记录
        if not self.log_text or message == self.last_log_message:
            return

        self.last_log_message = message
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{timestamp} - {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.status_var.set(message)

    def clear_logs(self):
        """清除日志内容"""
        if not self.log_text:
            return
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("日志已清空", "INFO")

    def start_bot(self):
        if not self.is_running:
            # 使用线程来执行测试连接，避免界面卡顿
            def test_connection_and_start():
                self.start_btn.config(state=tk.DISABLED)
                try:
                    # 测试AI引擎连接 (调用ai_tab的方法)
                    ai_engine_type = self.ai_tab.engine_var.get() # 从ai_tab的UI变量获取当前选中引擎
                    
                    connection_ok = False
                    result_message = ""

                    if ai_engine_type == "ollama":
                        connection_ok, result_message = self.ai_tab.test_ollama()
                    else: # deepseek
                        connection_ok, result_message = self.ai_tab.test_deepseek()
                    
                    if connection_ok:
                        self.root.after(0, lambda: messagebox.showinfo("连接成功", result_message))
                        self.root.after(0, self._finalize_start)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("连接失败", result_message))
                        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

                except Exception as e:
                    self.log_message(f"启动前测试连接出错: {str(e)}", "ERROR")
                    self.root.after(0, lambda: messagebox.showerror("错误", f"启动前测试连接出错: {str(e)}"))
                    self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))


            self.log_message("正在测试连接，请稍候...", "INFO")
            threading.Thread(target=test_connection_and_start, daemon=True).start()


    def _finalize_start(self):
        """连接测试完成后的处理"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.log_message("微信AI助手启动中...", "INFO")
        self.log_message(f"使用引擎: {self.config.get('ai_engine')}", "INFO")
        self.log_message(f"AI人设: {self.config.get('current_persona')}", "INFO")
        self.log_message(f"自动回复列表: {self.config.get('auto_reply_friends')}", "INFO")
        self.log_message("提示: 请确保在微信中打开了要监控的聊天窗口", "INFO")

        # 使用main.py中动态获取到的机器人昵称
        if self.bot_nickname:
            self.monitor.processor.set_bot_nickname(self.bot_nickname)
        else:
            self.log_message("未能获取机器人昵称，可能影响群聊@功能。", "WARNING")

        # 启动监控线程 (通过monitor实例)
        self.monitor.set_log_callback(self.log_message) # 将log_message传递给monitor
        
        # 确保monitor的test_connection方法能够通过MainWindow的log_message来记录日志
        self.monitor_thread = threading.Thread(target=self.monitor.start_monitoring, daemon=True)
        self.monitor_thread.start()

        self.log_message("微信AI助手已启动", "SUCCESS")

    def stop_bot(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.monitor.stop_monitoring() # 调用monitor的停止方法
            self.log_message("微信AI助手已停止", "INFO")

    def save_config(self):
        # 保存各标签页的配置到ConfigManager
        self.config.set("ai_engine", self.ai_tab.engine_var.get())
        self.config.set("ollama_host", self.ai_tab.ollama_host_var.get())
        self.config.set("ollama_model", self.ai_tab.ollama_model_var.get())
        self.config.set("deepseek_api_key", self.ai_tab.deepseek_key_var.get())

        self.config.set("auto_reply_friends", self.auto_reply_friends.get()) # 从auto_reply_friends获取值
        
        self.config.set("reply_when_mentioned", self.rules_tab.reply_when_mentioned.get())
        self.config.set("auto_reply_all", self.rules_tab.auto_reply_all.get())
        self.config.set("debug_mode", self.rules_tab.debug_mode.get())
        
        self.config.save_config() # 保存ConfigManager到文件
        self.log_message("配置已保存", "SUCCESS")


    def load_config(self):
        self.config.load_config() # 从文件加载ConfigManager
        # 将加载的配置分发给各标签页
        self.ai_tab.load_config()
        self.auto_reply_friends.set(self.config.get("auto_reply_friends", "女友,老婆,亲爱的")) # 设置auto_reply_friends的值
        # self.wechat_tab.load_config() # 移除wechat_tab的load_config调用
        self.rules_tab.load_config()
        self.log_message("配置已加载", "SUCCESS")

    def run(self):
        self.root.mainloop()

    def show_help(self):
        help_text = """
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
        """
        messagebox.showinfo("帮助", help_text)