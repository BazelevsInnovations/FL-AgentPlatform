import pytest

from fl_platform.executors.llm import StubLLMExecutor
from fl_platform.executors.base import ExecutorResult


@pytest.mark.asyncio
async def test_stub_executor():
    executor = StubLLMExecutor()
    result = await executor.execute(
        prompt="Test prompt",
        inputs={"key": "value"},
    )
    assert isinstance(result, ExecutorResult)
    assert "STUB" in result.content
    assert result.metadata.get("model") == "stub"


@pytest.mark.asyncio
async def test_stub_executor_with_system_prompt():
    executor = StubLLMExecutor()
    result = await executor.execute(
        prompt="Test",
        inputs={},
        system_prompt="You are a test agent.",
    )
    assert isinstance(result, ExecutorResult)
    assert result.content
