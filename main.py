from core.deepseek_client import DeepSeekClient
from core.ollama_client import OllamaClient
from service.message_monitor import MessageMonitor
from service.wechat_service import WeChatService
from ui.main_window import MainWindow
from config.config_manager import ConfigManager
import subprocess
import re
import sys

def get_wxauto_nickname_from_output():
    """通过运行子进程并捕获wxauto初始化输出，尝试获取机器人昵称。"""
    try:
        # 构建一个Python命令，用于在子进程中执行wxauto的初始化
        # 注意：这里我们只导入和初始化WeChat，不进行其他操作，以最小化副作用。
        # 我们将wxauto的初始化代码写成一个单行字符串，传递给-c参数
        wxauto_init_code = "from wxauto import WeChat; wx = WeChat()"
        
        # 使用subprocess运行这个Python命令，并捕获stdout
        # 设置timeout以防止进程卡住
        process = subprocess.run(
            [sys.executable, "-c", wxauto_init_code],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False, # 不抛出异常，以便我们可以检查stderr
            timeout=10 # 10秒超时
        )
        
        output = process.stdout + process.stderr # 捕获所有输出
        # print(f"[DEBUG] wxauto子进程原始输出: {output}") # 调试用，可取消注释

        # 使用正则表达式从输出中查找昵称
        match = re.search(r"初始化成功，获取到已登录窗口：(.*?)\n", output)
        if match:
            nickname = match.group(1).strip()
            if nickname:
                return nickname
        return None
    except subprocess.TimeoutExpired:
        print("[WARNING] wxauto子进程超时，未能获取到昵称。")
        return None
    except Exception as e:
        print(f"[ERROR] 从wxauto输出获取昵称时发生错误: {str(e)}")
        return None

def main():
    # 初始化配置
    config = ConfigManager()
    config.load_config()

    # 初始化AI引擎
    if config.get("ai_engine") == "ollama":
        ai_engine = OllamaClient(
            config.get("ollama_host"),
            config.get("ollama_model")
        )
    else:
        ai_engine = DeepSeekClient(config.get("deepseek_api_key"))

    # 初始化微信服务
    wechat_service = WeChatService()

    # 尝试动态获取机器人昵称
    bot_nickname = get_wxauto_nickname_from_output()
    if bot_nickname:
        print(f"[INFO] 成功动态获取机器人昵称: {bot_nickname}")
    else:
        print("[WARNING] 未能动态获取机器人昵称，将使用默认或可能不准确的昵称进行@识别。")
        # 如果无法动态获取，可以考虑设置一个备用昵称，例如从配置文件中获取或者设为"null"
        # 这里暂时不设置备用，让MessageProcessor自行处理未设置的情况

    # 初始化消息监控
    monitor = MessageMonitor(config, wechat_service, ai_engine)
    if bot_nickname: # 只有成功获取到昵称才设置
        monitor.processor.set_bot_nickname(bot_nickname)
    else:
        # 如果没有获取到动态昵称，但用户希望使用"null"，则手动设置
        # 或者让MessageProcessor继续使用其内部逻辑（如果它有默认值）
        pass # MessageProcessor会处理bot_nickname为None的情况

    # 初始化UI
    app = MainWindow(config, wechat_service, monitor, bot_nickname)
    app.run()


if __name__ == "__main__":
    main()