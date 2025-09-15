import os
import configparser
from typing import Any
from source.common.path_lib import CONFIG_PATH
from source.config.default_config import DEFAULT_CONFIG, get_default_value


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
        
        self.config_file = os.path.join(CONFIG_PATH, "config.ini")
        self.prompt_file = os.path.join(CONFIG_PATH, "prompt.txt")
        self.config = configparser.ConfigParser()
        self.prompt = ""
        self._ensure_config_dir()
        self._load_config()
        self._load_prompt()
        self._initialized = True
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH, exist_ok=True)
    
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
                self.config.read(self.config_file, encoding='utf-8')
            except Exception as e:
                print(f"警告: 加载配置文件失败: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        # 从默认配置字典创建配置项
        for section_name, section_data in DEFAULT_CONFIG.items():
            self.config.add_section(section_name)
            for key, config_item in section_data.items():
                value = config_item['value']
                self.config.set(section_name, key, str(value))
        
        self.save()
    
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
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
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
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
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
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
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
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if default is not None:
                return default
            # 尝试从默认配置获取
            return get_default_value(section, key, bool)
    
    def set(self, section: str, key: str, value: Any):
        """
        设置配置项
        
        Args:
            section: 配置节名
            key: 配置键名
            value: 配置值
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"错误: 保存配置文件失败: {e}")
    
    def reload(self):
        """重新加载配置文件"""
        self.config.clear()
        self._load_config()
    
    def has_section(self, section: str) -> bool:
        """检查是否存在指定配置节"""
        return self.config.has_section(section)
    
    def has_option(self, section: str, key: str) -> bool:
        """检查是否存在指定配置项"""
        return self.config.has_option(section, key)
    
    def get_sections(self) -> list:
        """获取所有配置节名"""
        return self.config.sections()
    
    def get_options(self, section: str) -> list:
        """获取指定配置节的所有键名"""
        try:
            return self.config.options(section)
        except configparser.NoSectionError:
            return []
    
    def remove_section(self, section: str):
        """删除配置节"""
        self.config.remove_section(section)
    
    def remove_option(self, section: str, key: str):
        """删除配置项"""
        self.config.remove_option(section, key)


# 创建全局配置实例
global_config = GlobalConfig()