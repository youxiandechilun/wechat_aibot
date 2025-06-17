import json
import os
from .constants import DEFAULT_CONFIG



class ConfigManager:
    def __init__(self, config_path="wechat_ai_config.json"):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config.update(json.load(f))
                return True
            return False
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            return False

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    def get_current_persona_description(self):
        current_persona_name = self.get("current_persona")
        personas = self.get("personas", [])
        for persona in personas:
            if persona.get("name") == current_persona_name:
                return persona.get("description", "")
        return ""

    def get_personas(self):
        return self.get("personas", [])

    def set_current_persona(self, persona_name):
        # 确保设置的当前人设存在于列表中
        personas = self.get("personas", [])
        if any(p.get("name") == persona_name for p in personas):
            self.set("current_persona", persona_name)
            self.save_config() # 立即保存配置

    def add_or_update_persona(self, name, description):
        personas = self.get("personas", [])
        found = False
        for persona in personas:
            if persona.get("name") == name:
                persona["description"] = description
                found = True
                break
        if not found:
            personas.append({"name": name, "description": description})
        self.set("personas", personas)
        self.save_config()

    def delete_persona(self, name):
        personas = self.get("personas", [])
        self.set("personas", [p for p in personas if p.get("name") != name])
        # 如果删除的是当前人设，则重置当前人设为空或第一个人设
        if self.get("current_persona") == name:
            self.set("current_persona", self.get("personas")[0]["name"] if self.get("personas") else "")
        self.save_config()