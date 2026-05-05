# utils/data_loader.py
import yaml
import json
import csv
from pathlib import Path
from common.logger import LoggerManager


logger = LoggerManager.get_logger()


def load_yaml(file_path):
    """
    加载YAML文件
    
    Args:
        file_path: YAML文件路径
        
    Returns:
        dict: 解析后的数据
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        logger.debug(f"成功加载YAML文件: {file_path}")
        return data or {}
    except Exception as e:
        logger.error(f"加载YAML文件失败: {str(e)}")
        return {}


def load_json(file_path):
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        dict: 解析后的数据
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug(f"成功加载JSON文件: {file_path}")
        return data
    except Exception as e:
        logger.error(f"加载JSON文件失败: {str(e)}")
        return {}


def load_csv(file_path, as_dict=True):
    """
    加载CSV文件
    
    Args:
        file_path: CSV文件路径
        as_dict: 是否返回字典列表，否则返回列表的列表
        
    Returns:
        list: 数据列表
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return []
        
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            if as_dict:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            else:
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
        
        logger.debug(f"成功加载CSV文件: {file_path}, 共 {len(data)} 行")
        return data
    except Exception as e:
        logger.error(f"加载CSV文件失败: {str(e)}")
        return []


def get_test_data(test_type, test_name, data_key=None):
    """
    获取测试数据
    
    Args:
        test_type: 测试类型 ('ui' 或 'api')
        test_name: 测试名称 (如 'login', 'course')
        data_key: 数据键（可选）
        
    Returns:
        dict/list: 测试数据
    """
    file_path = f"data/{test_type}/{test_name}_data.yaml"
    data = load_yaml(file_path)
    
    if data_key:
        return data.get(data_key, {})
    
    return data
