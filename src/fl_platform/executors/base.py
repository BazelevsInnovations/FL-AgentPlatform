from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExecutorResult:
    content: str = ""
    file_paths: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BaseExecutor(ABC):
    @abstractmethod
    async def execute(
        self,
        prompt: str,
        inputs: dict,
        *,
        model_id: str | None = None,
        system_prompt: str | None = None,
        extra_params: dict | None = None,
    ) -> ExecutorResult:
        ...
