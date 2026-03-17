import os
import uuid

import httpx

from fl_platform.executors.base import BaseExecutor, ExecutorResult


class FalVideoExecutor(BaseExecutor):
    def __init__(
        self, api_key: str, artifacts_dir: str, default_model: str = "fal-ai/minimax/video-01-live"
    ):
        self.api_key = api_key
        self.artifacts_dir = artifacts_dir
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
        params = {"prompt": prompt}
        if extra_params:
            params.update(extra_params)

        if not self.api_key:
            return ExecutorResult(
                content=f"[STUB VIDEO] model={model}, prompt={prompt[:100]}",
                metadata={"model": model, "stub": True},
            )

        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"https://fal.run/{model}",
                headers={
                    "Authorization": f"Key {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=params,
            )
            response.raise_for_status()
            data = response.json()

        video_url = data.get("video", {}).get("url", "")
        if not video_url:
            return ExecutorResult(content="No video returned", metadata=data)

        file_name = f"{uuid.uuid4().hex}.mp4"
        file_path = os.path.join(self.artifacts_dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        async with httpx.AsyncClient(timeout=120) as client:
            vid_response = await client.get(video_url)
            vid_response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(vid_response.content)

        return ExecutorResult(
            content=prompt,
            file_paths=[file_path],
            metadata={"model": model, "fal_response": data},
        )
