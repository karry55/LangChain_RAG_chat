"""Prompt 模板单元测试"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.rag.prompts import SYSTEM_PROMPT, QUERY_REWRITE_PROMPT


class TestSystemPrompt:
    """System Prompt 模板"""

    def test_system_prompt_not_empty(self):
        """System Prompt 不为空"""
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_context_placeholder(self):
        """包含 {context} 占位符"""
        assert "{context}" in SYSTEM_PROMPT

    def test_system_prompt_contains_history_placeholder(self):
        """包含 {history} 占位符"""
        assert "{history}" in SYSTEM_PROMPT

    def test_system_prompt_contains_question_placeholder(self):
        """包含 {question} 占位符"""
        assert "{question}" in SYSTEM_PROMPT

    def test_format_system_prompt(self):
        """格式化后生成完整 Prompt"""
        result = SYSTEM_PROMPT.format(
            context="参考资料：Mate 60 Pro 电池 5000mAh",
            history="用户: 你好",
            question="电池多大？",
        )
        assert "Mate 60 Pro" in result
        assert "你好" in result
        assert "电池多大？" in result
        assert "{" not in result  # 所有占位符已被替换

    def test_system_prompt_mentions_citation_rule(self):
        """包含引用规则说明"""
        assert "来源" in SYSTEM_PROMPT or "[来源" in SYSTEM_PROMPT

    def test_system_prompt_mentions_honesty(self):
        """包含诚实回答规则"""
        assert "无法回答" in SYSTEM_PROMPT or "没有足够信息" in SYSTEM_PROMPT


class TestQueryRewritePrompt:
    """查询重写 Prompt"""

    def test_query_rewrite_prompt_not_empty(self):
        """不为空"""
        assert len(QUERY_REWRITE_PROMPT) > 0

    def test_query_rewrite_contains_question_placeholder(self):
        """包含 {question} 占位符"""
        assert "{question}" in QUERY_REWRITE_PROMPT
