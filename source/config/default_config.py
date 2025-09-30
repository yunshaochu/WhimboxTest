#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
默认配置定义
"""

# 默认配置字典 - 整合了值、类型和描述信息
DEFAULT_CONFIG = {
    'General': {
        'debug': {
            'value': 'false',
            'type': bool,
            'description': '是否启用调试模式'
        },
        'cv_debug': {
            'value': 'false',
            'type': bool,
            'description': '是否启用CV调试模式'
        },
        'borderless_window': {
            'value': 'false',
            'type': bool,
            'description': '游戏是否为无边框窗口'
        },
        'ocr': {
            'value': 'rapid',
            'type': str,
            'description': 'OCR引擎，可选：rapid、paddle'
        }
    },
    'Agent': {
        'model':{
            'value': 'Qwen/Qwen3-30B-A3B-Instruct-2507',
            'type': str,
            'description': '模型名称'
        },
        'model_provider':{
            'value': 'openai',
            'type': str,
            'description': '模型提供商'
        },
        'base_url':{
            'value': 'https://api.siliconflow.cn/v1/',
            'type': str,
            'description': '模型API地址'
        },
        'api_key':{
            'value': '',
            'type': str,
            'description': '模型API密钥'
        }
    },
    'Game': {
        'energy_cost': {
            'value': '素材激化幻境',
            'type': str,
            'description': '默认消耗体力的幻境'
        },
        'meiyali_dig': {
            'value': '雾绡鱼|玉簪蚱蜢|画眉毛团|纯真丝线',
            'type': str,
            'description': '美鸭梨挖掘的默认材料（如果之前已经在挖掘，则沿用之前的）'
        },
        'jihua_target': {
            'value': '泡泡',
            'type': str,
            'description': '激化幻境的默认兑换目标'
        },
        'jihua_cost': {
            'value': '星荧草',
            'type': str,
            'description': '激化幻境的默认消耗材料'
        },
        'bless_target': {
            'value': '巨蛇遗迹试炼',
            'type': str,
            'description': '闪光幻境的默认目标试炼'
        }
    }
}


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
    except KeyError:
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


def get_config_type(section: str, key: str) -> type:
    """
    获取配置项的数据类型
    
    Args:
        section: 配置节名
        key: 配置键名
        
    Returns:
        配置项的数据类型，默认为str
    """
    try:
        return DEFAULT_CONFIG[section][key]['type']
    except KeyError:
        return str


