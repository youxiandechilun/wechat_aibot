import time
import threading
import collections
import re
import unicodedata # 新增导入
# from wxauto import elements # 移除此导入

from core.message_processor import MessageProcessor
# from utils.logger import Logger # 不再直接使用


class MessageMonitor:
    def __init__(self, config, wechat_service, ai_engine):
        self.config = config
        self.wechat_service = wechat_service
        self.processor = MessageProcessor(config, ai_engine) # 确保MessageProcessor可以接收log_callback
        # self.logger = Logger.get_logger() # 不再直接使用
        self.is_running = False
        self._log_callback = None # 用于接收主窗口的日志回调
        self._processed_message_history = collections.deque(maxlen=20) # 存储最近处理的标准化消息哈希值

    def set_log_callback(self, callback):
        self._log_callback = callback
        self.processor.set_log_callback(callback) # 将日志回调传递给MessageProcessor

    def _log(self, message, level="INFO"):
        if self._log_callback:
            self._log_callback(message, level)
        else:
            print(f"[{level}] {message}")

    def _normalize_message_for_comparison(self, sender, content):
        # 对字符串进行Unicode标准化 (NFKC)，以处理兼容性字符和组合字符
        normalized_sender_unicode = unicodedata.normalize('NFKC', str(sender))
        normalized_content_unicode = unicodedata.normalize('NFKC', str(content))

        # 显式地只保留字母、数字和中文字符，并转换为小写
        # 这比re.sub更严格，可以去除各种不可见或非核心字符
        cleaned_sender = ''.join(c for c in normalized_sender_unicode if c.isalnum() or ('\u4e00' <= c <= '\u9fa5')).lower()
        cleaned_content = ''.join(c for c in normalized_content_unicode if c.isalnum() or ('\u4e00' <= c <= '\u9fa5')).lower()
        
        # 返回标准化元组的哈希值
        return hash((cleaned_sender, cleaned_content))

    def start_monitoring(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def stop_monitoring(self):
        self.is_running = False

    def _monitor(self):
        self._log("开始监控微信消息...")

        while self.is_running:
            try:
                current_msg_obj = self.wechat_service.get_last_message() # 获取原始消息对象

                sender = None
                content = None
                current_message_content_hash = None

                # 优先检查是否为None
                if current_msg_obj is None:
                    time.sleep(0.5)
                    continue

                # 尝试从消息对象中提取发送者和内容
                # 假设wxauto消息对象有who和content属性
                if hasattr(current_msg_obj, 'sender') and hasattr(current_msg_obj, 'content'):
                    sender = current_msg_obj.sender
                    content = current_msg_obj.content
                    self._log(f"[Monitor DEBUG] 原始消息为wxauto对象格式, 通过.sender和.content获取信息。", "DEBUG")
                elif isinstance(current_msg_obj, (list, tuple)) and len(current_msg_obj) >= 2:
                    sender = current_msg_obj[0]
                    content = current_msg_obj[1]
                    self._log(f"[Monitor DEBUG] 原始消息为元组/列表格式，发送者: {sender}", "DEBUG")
                else:
                    # 对于所有其他类型 (包括不含sender/content属性的wxauto对象和字符串)，统一视为Self消息，并尝试提取内容
                    sender = "Self"
                    content = str(current_msg_obj) # 尝试使用str()获取内容作为兜底
                    self._log(f"[Monitor DEBUG] 原始消息为非预期格式，回退到str()获取内容。推定发送者为: {sender}", "DEBUG")
                    self._log(f"[Monitor DEBUG] 原始消息对象类型: {type(current_msg_obj)}", "DEBUG")
                    self._log(f"[Monitor DEBUG] 原始消息对象dir(): {dir(current_msg_obj)}", "DEBUG")
                    try:
                        self._log(f"[Monitor DEBUG] 原始消息对象vars(): {vars(current_msg_obj)}", "DEBUG")
                    except TypeError:
                        self._log("[Monitor DEBUG] 原始消息对象不支持vars()", "DEBUG")
                
                # 如果成功提取了sender和content，进行标准化和哈希
                if sender is not None and content is not None:
                    current_message_content_hash = self._normalize_message_for_comparison(sender, content)

                # 核心去重逻辑：如果当前标准化消息哈希值不在历史记录中，则处理
                if current_message_content_hash is not None and current_message_content_hash not in self._processed_message_history:
                    # 所有消息相关的调试日志和处理，现在都在这个if块内部
                    self._log(f"[Monitor DEBUG] 从WeChatService获取的原始消息对象: {current_msg_obj}", "DEBUG")
                    
                    self._log(f"[Monitor DEBUG] 标准化后的消息哈希值: {current_message_content_hash}", "DEBUG")
                    self._log(f"[Monitor DEBUG] 当前历史哈希队列: {list(self._processed_message_history)}", "DEBUG")
                    self._log(f"[Monitor DEBUG] 消息哈希不在历史记录中，准备处理。", "DEBUG")

                    self._processed_message_history.append(current_message_content_hash) # 添加哈希值到历史记录

                    # 在这里统一控制日志输出
                    debug_mode = self.config.get("debug_mode", False) # 从config获取debug_mode

                    is_filtered_sender = (sender in ["SYS", "Time", "System", "null", "Self"] or not sender)

                    # 记录"收到消息"日志
                    if not is_filtered_sender or debug_mode:
                        self._log(f"收到消息 - 发送人: '{sender}', 内容: '{content}'", "INFO")

                    # 判断是否应该回复
                    if self.processor.should_reply(sender, content):
                        # 记录"符合回复条件"日志
                        if not is_filtered_sender:
                            self._log(f"消息符合回复条件，准备回复 - 发送人: '{sender}'", "INFO")
                        self._process_message(current_msg_obj) # 只有符合条件才处理消息
                    else:
                        # 记录"忽略消息"日志
                        if not is_filtered_sender or debug_mode:
                            self._log(f"忽略消息 (不符合回复条件) - 发送人: '{sender}', 内容: '{content}'", "DEBUG")
                # 如果哈希已在历史记录中，则不输出任何日志
                
                time.sleep(0.5) # 每次循环的通用等待时间

            except Exception as e:
                self._log(f"监控出错: {str(e)}", "ERROR")
                time.sleep(3)

    def _process_message(self, msg):
        response = self.processor.process_message(msg)
        if response:
            self.wechat_service.send_message(response)
            self._log(f"已发送回复: {response}", "INFO")