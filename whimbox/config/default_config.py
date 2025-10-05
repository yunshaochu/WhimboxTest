#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
默认配置定义
"""

import os, json
from whimbox.common.path_lib import ASSETS_PATH

# 默认配置字典 - 整合了值、类型和描述信息
DEFAULT_CONFIG = json.load(open(os.path.join(ASSETS_PATH, 'default_config.json'), 'r', encoding='utf-8'))


def get_default_value(section: str, key: str, value_type: type = str):
    """
    获取指定配置项的默认值
    
    Args:
        section: 配置节名
        key: 配置键名
        value_type: 期望的值类型
        
    Returns:
        默认值，如果不存在则返回类型的默认值
    """
    try:
        config_item = DEFAULT_CONFIG[section][key]
        value = config_item['value']
        
        # 根据类型转换
        if value_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif value_type == int:
            return int(value)
        elif value_type == float:
            return float(value)
        else:
            return str(value)
    except Exception as e:
        # 返回类型的默认值
        if value_type == bool:
            return False
        elif value_type == int:
            return 0
        elif value_type == float:
            return 0.0
        else:
            return ""


def get_config_description(section: str, key: str) -> str:
    """
    获取配置项的描述信息
    
    Args:
        section: 配置节名
        key: 配置键名
        
    Returns:
        配置项描述，如果不存在则返回空字符串
    """
    try:
        return DEFAULT_CONFIG[section][key]['description']
    except KeyError:
        return ""


