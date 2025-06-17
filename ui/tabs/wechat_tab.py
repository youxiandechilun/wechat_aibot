import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from service.wechat_service import WeChatService


class WechatTab(ttk.Frame):
    def __init__(self, notebook, log_callback, wechat_service, auto_reply_friends_var):
        super().__init__(notebook, padding=10)
        self.log_message = log_callback
        self.wechat_service = wechat_service
        self.auto_reply_friends = auto_reply_friends_var
        self.setup_ui()

    def setup_ui(self):
        # 微信联系人设置框架
        wechat_frame = ttk.LabelFrame(self, text="微信联系人设置", padding=10)
        wechat_frame.pack(fill=tk.X, pady=5)

        # 自动回复的好友
        ttk.Label(wechat_frame, text="自动回复的好友:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(wechat_frame, textvariable=self.auto_reply_friends, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(wechat_frame, text="多个好友用逗号分隔").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        # 自动回复的群聊
        ttk.Label(wechat_frame, text="自动回复的群聊:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.group_list = tk.Listbox(wechat_frame, height=5, width=50)
        self.group_list.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # 群聊操作按钮
        btn_frame = ttk.Frame(wechat_frame)
        btn_frame.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

        ttk.Button(btn_frame, text="刷新群列表", command=self.refresh_groups).pack(pady=2)
        ttk.Button(btn_frame, text="添加选中群", command=self.add_selected_group).pack(pady=2)
        ttk.Button(btn_frame, text="清空列表", command=self.clear_groups).pack(pady=2)

    def refresh_groups(self):
        def _refresh():
            try:
                # 获取所有会话
                sessions_dict = self.wechat_service.get_session_list() # 获取到的sessions是一个字典
                self.log_message(f"[DEBUG] refresh_groups: GetSessionList原始会话对象: {sessions_dict}", "DEBUG")
                
                groups = []
                for name, _ in sessions_dict.items():
                    self.log_message(f"[DEBUG] Processing session name: '{name}' (type: {type(name)})", "DEBUG")
                    
                    # 判断是否是群聊，根据名称中是否包含顿号'、'或逗号','以及成员数量
                    # 这里的判断可能需要根据实际wxauto返回的群聊名称格式进行调整
                    is_group_by_separator = '、' in name or ',' in name
                    is_group_by_parentheses = '(' in name and ')' in name
                    
                    self.log_message(f"[DEBUG]   is_group_by_separator: {is_group_by_separator}, is_group_by_parentheses: {is_group_by_parentheses}", "DEBUG")

                    if is_group_by_separator or is_group_by_parentheses:
                        # 进一步检查名称是否包含多个成员（例如通过拆分，如果拆分后不止一个元素）
                        has_multiple_members = False
                        if '、' in name:
                            if len(name.split('、')) > 1:
                                has_multiple_members = True
                        if ',' in name: # Check for comma even if '、' was found, as a fallback/additional check
                            if len(name.split(',')) > 1:
                                has_multiple_members = True

                        self.log_message(f"[DEBUG]   has_multiple_members: {has_multiple_members}", "DEBUG")

                        if has_multiple_members:
                            groups.append(name)
                            self.log_message(f"[DEBUG]   Added group: '{name}'", "DEBUG")

                self.group_list.delete(0, tk.END)
                for group in groups:
                    self.group_list.insert(tk.END, group)

                self.log_message(f"已刷新群列表，找到 {len(groups)} 个群聊", "INFO")
            except Exception as e:
                self.log_message(f"刷新群列表失败: {str(e)}", "ERROR")

        # 使用线程来执行刷新操作，避免界面卡顿
        threading.Thread(target=_refresh, daemon=True).start()

    def add_selected_group(self):
        selected = self.group_list.curselection()
        if not selected:
            return

        selected_group = self.group_list.get(selected[0])
        current_friends = self.auto_reply_friends.get()

        if selected_group not in current_friends:
            if current_friends:
                new_friends = current_friends + "," + selected_group
            else:
                new_friends = selected_group

            self.auto_reply_friends.set(new_friends)
            self.log_message(f"已添加群聊: {selected_group}", "SUCCESS")

    def clear_groups(self):
        self.auto_reply_friends.set("")
        self.log_message("已清空自动回复列表", "INFO")