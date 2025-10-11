import os
import configparser
import shutil
from typing import Any
import json
from whimbox.common.path_lib import CONFIG_PATH, ASSETS_PATH
from whimbox.config.default_config import DEFAULT_CONFIG, get_default_value


class GlobalConfig:
    """
    配置管理类
    支持INI格式配置文件的读写操作
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(GlobalConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化配置管理器
        """
        if self._initialized:
            return
        
        self.config_file = os.path.join(CONFIG_PATH, "config.json")
        self.prompt_file = os.path.join(CONFIG_PATH, "prompt.txt")
        self.config = {}
        self.prompt = ""
        self._update_user_config()
        self._load_config()
        self._load_prompt()
        self._initialized = True
    
    def _update_user_config(self):
        """确保配置目录存在，并检查新增的默认配置项"""
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH, exist_ok=True)

        # 如果配置不存在，就直接复制默认配置
        if not os.path.exists(self.config_file):
            shutil.copy2(os.path.join(ASSETS_PATH, "default_config.json"), self.config_file)
        else:
            # 如果配置存在，就检查新增的默认配置项
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            for section_name, section_data in DEFAULT_CONFIG.items():
                if section_name not in user_config:
                    user_config[section_name] = {}
                for key, config_item in section_data.items():
                    if key not in user_config[section_name]:
                        user_config[section_name][key] = config_item
                    else:
                        user_config[section_name][key]['description'] = config_item['description']
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(user_config, f, ensure_ascii=False, indent=4)

        # 如果提示词不存在，就直接复制默认提示词
        if not os.path.exists(self.prompt_file):
            shutil.copy2(os.path.join(ASSETS_PATH, "default_prompt.txt"), self.prompt_file)
    
    def _load_prompt(self):
        """加载提示词文件"""
        if os.path.exists(self.prompt_file):
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                self.prompt = f.read()
        else:
            self.prompt = ""

    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"警告: 加载配置文件失败: {e}")
                self.config = {}
        else:
            self.config = {}
    
    def get(self, section: str, key: str, default: Any = None) -> str:
        """
        获取配置项的字符串值
        
        Args:
            section: 配置节名
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            return self.config[section][key]['value']
        except KeyError:
            if default is not None:
                return str(default)
            # 尝试从默认配置获取
            return get_default_value(section, key, str)
    
    def get_int(self, section: str, key: str, default: int = None) -> int:
        """
        获取配置项的整数值
        
        Args:
            section: 配置节名
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            return int(self.config[section][key]['value'])
        except Exception as e:
            if default is not None:
                return default
            # 尝试从默认配置获取
            return get_default_value(section, key, int)
    
    def get_float(self, section: str, key: str, default: float = None) -> float:
        """
        获取配置项的浮点数值
        
        Args:
            section: 配置节名
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            return float(self.config[section][key]['value'])
        except Exception as e:
            if default is not None:
                return default
            # 尝试从默认配置获取
            return get_default_value(section, key, float)
    
    def get_bool(self, section: str, key: str, default: bool = None) -> bool:
        """
        获取配置项的布尔值
        
        Args:
            section: 配置节名
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            return self.config[section][key]['value'].lower() in ('true', '1', 'yes', 'on')
        except Exception as e:
            if default is not None:
                return default
            # 尝试从默认配置获取
            return get_default_value(section, key, bool)
    

    def set(self, section: str, key: str, value: Any) -> None:
        """设置配置项的值"""
        if section not in self.config:
            self.config[section] = {}
        if key not in self.config[section]:
            self.config[section][key] = {}
        
        # 保持描述信息
        description = self.config[section][key].get('description', '')
        if not description and section in DEFAULT_CONFIG and key in DEFAULT_CONFIG[section]:
            description = DEFAULT_CONFIG[section][key].get('description', '')
        
        self.config[section][key] = {
            'value': value,
            'description': description
        }

    def save(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            return False

    def reload(self) -> None:
        """重新加载配置文件"""
        self._load_config()

# 创建全局配置实例
global_config = GlobalConfig()

if __name__ == "__main__":
    print(global_config.get("Game", "energy_cost"))