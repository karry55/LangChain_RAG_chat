"""pytest 全局配置"""
import pytest
import sys
import os

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
