import tkinter as tk
from tkinter import ttk, messagebox
import requests
import openai

from core.deepseek_client import DeepSeekClient
from core.ollama_client import OllamaClient


class AITab:
    def __init__(self, parent, config, log_callback=None):
        self.config = config
        self.frame = ttk.Frame(parent, padding=10)
        self._log = log_callback if log_callback else print # 使用传入的log_callback，如果没有则退回print

        # 用于绑定当前选中人设的变量
        self.current_persona_name_var = tk.StringVar()
        self.edit_persona_name_var = tk.StringVar()
        
        self.setup_ui()
        self.load_config() # 在初始化时加载配置

    def setup_ui(self):
        # AI引擎设置区域
        ai_frame = ttk.LabelFrame(self.frame, text="AI引擎设置", padding=10)
        ai_frame.pack(fill=tk.X, pady=5)

        # AI引擎选择
        engine_frame = ttk.Frame(ai_frame)
        engine_frame.pack(fill=tk.X, pady=5)
        ttk.Label(engine_frame, text="选择AI引擎:").pack(side=tk.LEFT, padx=5)
        self.engine_var = tk.StringVar(value=self.config.get("ai_engine", "ollama"))
        ttk.Radiobutton(engine_frame, text="Ollama (本地)", variable=self.engine_var, value="ollama").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(engine_frame, text="DeepSeek (在线)", variable=self.engine_var, value="deepseek").pack(side=tk.LEFT, padx=5)

        # Ollama配置
        ollama_frame = ttk.LabelFrame(ai_frame, text="Ollama配置", padding=10)
        ollama_frame.pack(fill=tk.X, pady=5)
        self.ollama_host_var = tk.StringVar(value=self.config.get("ollama_host", "http://localhost:11434"))
        self.ollama_model_var = tk.StringVar(value=self.config.get("ollama_model", "deepseek-r1:8b"))
        ttk.Label(ollama_frame, text="API地址:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(ollama_frame, textvariable=self.ollama_host_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(ollama_frame, text="模型名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(ollama_frame, textvariable=self.ollama_model_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(ollama_frame, text="测试连接", command=self.test_ollama).grid(row=1, column=2, padx=5)

        # DeepSeek配置
        deepseek_frame = ttk.LabelFrame(ai_frame, text="DeepSeek配置", padding=10)
        deepseek_frame.pack(fill=tk.X, pady=5)
        self.deepseek_key_var = tk.StringVar(value=self.config.get("deepseek_api_key", ""))
        ttk.Label(deepseek_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(deepseek_frame, textvariable=self.deepseek_key_var, width=40, show="*").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(deepseek_frame, text="测试连接", command=self.test_deepseek).grid(row=0, column=2, padx=5)

        # AI人设设置 (新)
        persona_manage_frame = ttk.LabelFrame(ai_frame, text="AI人设管理", padding=10)
        persona_manage_frame.pack(fill=tk.X, pady=5)

        # 当前人设选择
        current_persona_frame = ttk.Frame(persona_manage_frame)
        current_persona_frame.pack(fill=tk.X, pady=5)
        ttk.Label(current_persona_frame, text="当前人设:").pack(side=tk.LEFT, padx=5)
        self.persona_name_combo = ttk.Combobox(current_persona_frame, textvariable=self.current_persona_name_var, width=25)
        self.persona_name_combo.pack(side=tk.LEFT, padx=5)
        self.persona_name_combo.bind("<<ComboboxSelected>>", self._on_persona_selected)
        self.persona_name_combo.bind("<Button-1>", self._update_persona_list_ui) # 点击时更新列表

        # 人设编辑区
        edit_persona_frame = ttk.LabelFrame(persona_manage_frame, text="编辑人设", padding=10)
        edit_persona_frame.pack(fill=tk.X, pady=5)

        ttk.Label(edit_persona_frame, text="人设名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(edit_persona_frame, textvariable=self.edit_persona_name_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(edit_persona_frame, text="人设描述:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=2)
        self.edit_persona_description_text = tk.Text(edit_persona_frame, height=5, width=50)
        self.edit_persona_description_text.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # 按钮
        persona_buttons_frame = ttk.Frame(edit_persona_frame)
        persona_buttons_frame.grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(persona_buttons_frame, text="新建/更新人设", command=self._add_or_update_persona).pack(side=tk.LEFT, padx=5)
        ttk.Button(persona_buttons_frame, text="删除人设", command=self._delete_persona).pack(side=tk.LEFT, padx=5)
        ttk.Button(persona_buttons_frame, text="设为当前", command=self._set_as_current_persona).pack(side=tk.LEFT, padx=5)


    def load_config(self):
        # 从ConfigManager加载人设列表和当前选中人设
        self._update_persona_list_ui() # 刷新人设下拉列表
        current_persona_name = self.config.get("current_persona", "")
        self.current_persona_name_var.set(current_persona_name)
        self._on_persona_selected() # 加载当前选中人设的描述

        # 加载AI引擎配置
        self.engine_var.set(self.config.get("ai_engine", "ollama"))
        self.ollama_host_var.set(self.config.get("ollama_host", "http://localhost:11434"))
        self.ollama_model_var.set(self.config.get("ollama_model", "deepseek-r1:8b"))
        self.deepseek_key_var.set(self.config.get("deepseek_api_key", ""))

    def _update_persona_list_ui(self, event=None):
        """刷新人设下拉列表，并设置当前选中的人设。"""
        personas = self.config.get_personas()
        persona_names = [p["name"] for p in personas]
        self.persona_name_combo["values"] = persona_names
        
        # 尝试设置当前选中的人设，如果config中记录的当前人设不在列表中，则清空
        current_name = self.config.get("current_persona", "")
        if current_name in persona_names:
            self.current_persona_name_var.set(current_name)
        elif persona_names:
            # 如果原先的当前人设不存在，则默认选择第一个人设
            self.current_persona_name_var.set(persona_names[0])
            self.config.set_current_persona(persona_names[0]) # 更新ConfigManager
        else:
            self.current_persona_name_var.set("") # 没有人设时清空

    def _on_persona_selected(self, event=None):
        """当人设在下拉框中被选中时，加载其名称和描述到编辑区。"""
        selected_name = self.current_persona_name_var.get()
        if not selected_name:
            self.edit_persona_name_var.set("")
            self.edit_persona_description_text.delete("1.0", tk.END)
            return

        personas = self.config.get_personas()
        for persona in personas:
            if persona["name"] == selected_name:
                self.edit_persona_name_var.set(persona["name"])
                self.edit_persona_description_text.delete("1.0", tk.END)
                self.edit_persona_description_text.insert(tk.END, persona["description"])
                break

    def _add_or_update_persona(self):
        """添加或更新人设。"""
        name = self.edit_persona_name_var.get().strip()
        description = self.edit_persona_description_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("错误", "人设名称不能为空！")
            return
        if not description:
            messagebox.showwarning("警告", "人设描述为空，可能会影响AI表现。")

        self.config.add_or_update_persona(name, description)
        self._log(f"人设 '{name}' 已保存。", "SUCCESS")
        self._update_persona_list_ui() # 刷新列表
        self.current_persona_name_var.set(name) # 设为当前选中
        self._set_as_current_persona() # 立即设为当前人设

    def _delete_persona(self):
        """删除当前编辑区显示的人设。"""
        name_to_delete = self.edit_persona_name_var.get().strip()
        if not name_to_delete:
            messagebox.showwarning("提示", "请选择要删除的人设。")
            return

        if messagebox.askyesno("确认删除", f"确定要删除人设 '{name_to_delete}' 吗？"):
            self.config.delete_persona(name_to_delete)
            self._log(f"人设 '{name_to_delete}' 已删除。", "INFO")
            self._update_persona_list_ui() # 刷新列表
            self.edit_persona_name_var.set("")
            self.edit_persona_description_text.delete("1.0", tk.END)

    def _set_as_current_persona(self):
        """将当前编辑区显示的人设设为当前活跃人设。"""
        selected_name = self.edit_persona_name_var.get().strip()
        if not selected_name:
            messagebox.showwarning("提示", "请选择一个人设设为当前。")
            return
        
        personas = self.config.get_personas()
        if not any(p['name'] == selected_name for p in personas):
            messagebox.showerror("错误", "该人设不存在，请先保存。")
            return

        self.config.set_current_persona(selected_name)
        self.current_persona_name_var.set(selected_name) # 更新下拉框显示
        self._log(f"当前人设已设置为 '{selected_name}'。", "SUCCESS")

    def test_ollama(self):
        host = self.ollama_host_var.get()
        model = self.ollama_model_var.get()
        client = OllamaClient(host, model)
        try:
            self._log("正在测试Ollama连接...", "INFO")
            if client.test_connection():
                available_models = [m['name'] for m in client.get_available_models()]
                msg = f"Ollama连接成功! 可用模型:\n{', '.join(available_models)}"
                self._log(msg, "SUCCESS")
                return True, msg
            else:
                msg = "Ollama连接失败，请检查API地址和模型名称！"
                self._log(msg, "ERROR")
                return False, msg
        except Exception as e:
            msg = f"Ollama连接错误: {str(e)}"
            self._log(msg, "ERROR")
            return False, msg

    def test_deepseek(self):
        api_key = self.deepseek_key_var.get().strip()
        if not api_key:
            msg = "DeepSeek API密钥不能为空"
            self._log(msg, "ERROR")
            return False, msg
        client = DeepSeekClient(api_key)
        try:
            self._log("正在测试DeepSeek连接...", "INFO")
            if client.test_connection():
                msg = "DeepSeek连接成功!"
                self._log(msg, "SUCCESS")
                return True, msg
            else:
                msg = "DeepSeek连接失败，请检查API密钥！"
                self._log(msg, "ERROR")
                return False, msg
        except Exception as e:
            msg = f"DeepSeek连接错误: {str(e)}"
            self._log(msg, "ERROR")
            return False, msg