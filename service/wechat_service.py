import time
from wxauto import WeChat


class WeChatService:
    def __init__(self):
        self._log_callback = None  # 确保在任何其他属性访问之前初始化
        self.wx = WeChat()  # 严格按照root.py的方式初始化

    def set_log_callback(self, callback):
        self._log_callback = callback

    def _log(self, message, level="INFO"):
        if self._log_callback:
            self._log_callback(message, level)
        else:
            print(f"[{level}] {message}")

    def get_session_list(self):
        try:
            self._log("正在获取会话列表...", "DEBUG")
            sessions = self.wx.GetSessionList()
            self._log(f"获取到 {len(sessions)} 个会话", "DEBUG")
            return sessions
        except Exception as e:
            self._log(f"获取会话列表失败: {str(e)}", "ERROR")
            self._log("请确保微信客户端已打开并登录，且wxauto库与您的微信版本兼容。", "WARNING")
            return []

    def get_all_chat_names(self):
        try:
            self._log("正在获取所有聊天名称...", "DEBUG")
            sessions = self.wx.GetSessionList()
            self._log(f"[DEBUG] GetSessionList返回的原始会话列表: {sessions}", "DEBUG")
            
            return list(sessions.keys())
        except Exception as e:
            self._log(f"获取所有聊天名称失败: {str(e)}", "ERROR")
            self._log("请确保微信客户端已打开并登录，且wxauto库与您的微信版本兼容。", "WARNING")
            return []

    def get_last_message(self):
        try:
            current_msg = self.wx.GetLastMessage
            return current_msg
        except AttributeError:
            try:
                msgs = self.wx.GetAllMessage()
                return msgs[-1] if msgs else None
            except Exception as e:
                self._log(f"获取最后一条消息失败: {str(e)}", "ERROR")
                self._log("请确保微信客户端已打开并登录，且wxauto库与您的微信版本兼容。", "WARNING")
                return None
        except Exception as e:
            self._log(f"获取最后一条消息失败 (通用错误): {str(e)}", "ERROR")
            self._log("请确保微信客户端已打开并登录，且wxauto库与您的微信版本兼容。", "WARNING")
            return None

    def send_message(self, message):
        try:
            self.wx.SendMsg(message)
            self._log(f"已通过微信发送消息: {message}", "DEBUG")
        except Exception as e:
            self._log(f"发送微信消息失败: {str(e)}", "ERROR")
            self._log("请确保微信客户端已打开并登录，且wxauto库与您的微信版本兼容。", "WARNING")