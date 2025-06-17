import unicodedata
import re

class MessageProcessor:
    def __init__(self, config_manager, ai_engine):
        self.config = config_manager
        self.ai_engine = ai_engine
        self._log_callback = None
        self.bot_nickname = None # Initialize bot_nickname

    def set_log_callback(self, callback):
        self._log_callback = callback

    def set_bot_nickname(self, nickname):
        """设置机器人的昵称，用于在群聊中识别@消息。"""
        self.bot_nickname = nickname
        self._log(f"MessageProcessor已设置机器人昵称: {self.bot_nickname}", "DEBUG")

    def _log(self, message, level="INFO"):
        if self._log_callback:
            self._log_callback(message, level)
        else:
            print(f"[{level}] {message}")

    def should_reply(self, sender, content):
        # 1. 过滤机器人自己发送的消息 (非常重要，避免循环回复)
        if self.bot_nickname and sender == self.bot_nickname:
            self._log(f"忽略消息 (机器人自身发送): 发送人: '{sender}', 内容: '{content}'", "DEBUG")
            return False

        # 2. 过滤系统消息和无效发送者
        if sender in ["SYS", "Time", "System", "null", "Self"] or not sender:
            self._log(f"忽略消息 (系统/无效发送者): 发送人: '{sender}', 内容: '{content}'", "DEBUG")
            return False

        # 3. 全局自动回复所有消息模式 (优先级最高)
        if self.config.get("auto_reply_all", False):
            self._log(f"回复消息 (全局自动回复): 发送人: '{sender}', 内容: '{content}'", "DEBUG")
            return True

        # 4. 获取自动回复列表 (私聊好友和被监控群聊)
        # auto_reply_friends现在包含了希望自动回复的私聊好友和要监控的群聊名称
        auto_reply_list = [name.strip().lower()
                           for name in self.config.get("auto_reply_friends", "").split(",")
                           if name.strip()]

        # 5. 判断是否是群聊 (更灵活的判断方式，与wechat_tab保持一致)
        is_group_chat = False
        if '、' in sender or ',' in sender or ('(' in sender and ')' in sender):
            # 进一步检查名称是否包含多个成员
            # 这里简化判断，只要有分隔符或括号，就认为是群聊
            is_group_chat = True
        
        # 6. 群聊消息处理
        if is_group_chat:
            self._log(f"处理群聊消息: 发送人: '{sender}', 内容: '{content}'", "DEBUG")
            
            # 检查是否开启"群聊中仅回复@我的消息"
            if self.config.get("reply_when_mentioned", True):
                # 检查是否@机器人
                if self.bot_nickname and f"@{self.bot_nickname.lower()}" in content.lower():
                    self._log(f"回复群聊消息 (@机器人): 发送人: '{sender}', 内容: '{content}'", "INFO")
                    return True
                # 检查是否@所有人
                if "@所有人" in content:
                    self._log(f"回复群聊消息 (@所有人): 发送人: '{sender}', 内容: '{content}'", "INFO")
                    return True
                self._log(f"忽略群聊消息 (未@机器人且'仅回复@'开启): 发送人: '{sender}', 内容: '{content}'", "DEBUG")
                return False
            else:
                # 如果'仅回复@'未开启，且群聊在监控列表，则回复所有消息
                if sender.lower() in auto_reply_list:
                    self._log(f"回复群聊消息 (未@机器人但群聊在回复列表): 发送人: '{sender}', 内容: '{content}'", "INFO")
                    return True
                self._log(f"忽略群聊消息 (未@机器人且群聊不在回复列表): 发送人: '{sender}', 内容: '{content}'", "DEBUG")
                return False

        # 7. 私聊消息处理
        # 只有当消息来自私聊，并且发送者在auto_reply_list中时才回复
        if sender.lower() in auto_reply_list:
            self._log(f"回复私聊消息: 发送人: '{sender}', 内容: '{content}'", "INFO")
            return True
        
        self._log(f"忽略消息 (不符合回复条件): 发送人: '{sender}', 内容: '{content}'", "DEBUG")
        return False

    def process_message(self, msg_obj):
        # Extract sender and content from the message object
        sender = None
        content = None
        
        if hasattr(msg_obj, 'sender') and hasattr(msg_obj, 'content'):
            sender = msg_obj.sender
            content = msg_obj.content
        elif isinstance(msg_obj, (list, tuple)) and len(msg_obj) >= 2:
            sender = msg_obj[0]
            content = msg_obj[1]
        else:
            # Fallback: if cannot extract sender/content, log and return None
            self._log(f"无法从消息对象提取发送者和内容，消息对象类型: {type(msg_obj)}, 内容: {str(msg_obj)}", "ERROR")
            return None # Do not proceed if sender/content cannot be reliably determined

        # Now pass the extracted sender and content to should_reply
        if not self.should_reply(sender, content):
            return None

        persona_desc = self.config.get_current_persona_description()
        
        final_ai_input = content
        if persona_desc:
            # 这里的ai_persona配置已废弃，直接使用persona_desc作为AI的引导语
            final_ai_input = f"（请以以下人设回复：{persona_desc}）{content}"

        return self.ai_engine.get_response(final_ai_input, persona_desc)