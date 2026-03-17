import json

import anthropic
import openai

from fl_platform.executors.base import BaseExecutor, ExecutorResult


class LLMExecutor(BaseExecutor):
    def __init__(self, provider: str, api_key: str, default_model: str | None = None):
        self.provider = provider
        self.api_key = api_key
        self.default_model = default_model

    async def execute(
        self,
        prompt: str,
        inputs: dict,
        *,
        model_id: str | None = None,
        system_prompt: str | None = None,
        extra_params: dict | None = None,
    ) -> ExecutorResult:
        model = model_id or self.default_model

        user_message = self._build_user_message(prompt, inputs)

        if self.provider == "claude":
            return await self._call_claude(user_message, system_prompt, model, extra_params)
        elif self.provider == "openai":
            return await self._call_openai(user_message, system_prompt, model, extra_params)
        else:
            return await self._call_stub(user_message, system_prompt)

    def _build_user_message(self, prompt: str, inputs: dict) -> str:
        parts = []
        if prompt:
            parts.append(prompt)
        for key, value in inputs.items():
            if isinstance(value, dict):
                parts.append(f"## {key}\n```json\n{json.dumps(value, ensure_ascii=False, indent=2)}\n```")
            else:
                parts.append(f"## {key}\n{value}")
        return "\n\n".join(parts)

    async def _call_claude(
        self, user_message: str, system_prompt: str | None, model: str | None, extra_params: dict | None
    ) -> ExecutorResult:
        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        params = {
            "model": model or "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": user_message}],
        }
        if system_prompt:
            params["system"] = system_prompt
        if extra_params:
            params.update(extra_params)

        response = await client.messages.create(**params)
        content = response.content[0].text
        return ExecutorResult(
            content=content,
            metadata={
                "model": response.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )

    async def _call_openai(
        self, user_message: str, system_prompt: str | None, model: str | None, extra_params: dict | None
    ) -> ExecutorResult:
        client = openai.AsyncOpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        params = {
            "model": model or "gpt-4o",
            "messages": messages,
            "max_tokens": 4096,
        }
        if extra_params:
            params.update(extra_params)

        response = await client.chat.completions.create(**params)
        content = response.choices[0].message.content or ""
        return ExecutorResult(
            content=content,
            metadata={
                "model": response.model,
                "input_tokens": getattr(response.usage, "prompt_tokens", 0),
                "output_tokens": getattr(response.usage, "completion_tokens", 0),
            },
        )

    async def _call_stub(self, user_message: str, system_prompt: str | None) -> ExecutorResult:
        return ExecutorResult(
            content=f'[STUB LLM] Received {len(user_message)} chars. System prompt: {bool(system_prompt)}',
            metadata={"model": "stub", "input_tokens": 0, "output_tokens": 0},
        )


class StubLLMExecutor(BaseExecutor):
    async def execute(
        self,
        prompt: str,
        inputs: dict,
        *,
        model_id: str | None = None,
        system_prompt: str | None = None,
        extra_params: dict | None = None,
    ) -> ExecutorResult:
        return ExecutorResult(
            content=f'[STUB] Prompt: {prompt[:100]}... Inputs: {list(inputs.keys())}',
            metadata={"model": "stub"},
        )
