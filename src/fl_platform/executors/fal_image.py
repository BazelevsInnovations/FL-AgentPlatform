import os
import uuid

import httpx

from fl_platform.executors.base import BaseExecutor, ExecutorResult


class FalImageExecutor(BaseExecutor):
    def __init__(self, api_key: str, artifacts_dir: str, default_model: str = "fal-ai/nano-banana-2"):
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

        # Collect reference image file paths from inputs
        ref_images = []
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("[file:") and value.endswith("]"):
                file_path = value[6:-1]
                if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    ref_images.append(file_path)

        if not self.api_key:
            stub_refs = f", refs={len(ref_images)}" if ref_images else ""
            return ExecutorResult(
                content=f"[STUB IMAGE] model={model}, prompt={prompt[:100]}{stub_refs}",
                metadata={"model": model, "stub": True, "ref_images": len(ref_images)},
            )

        # Upload reference images and set image_url if available
        if ref_images and "image_url" not in params:
            # Upload first reference image to get a URL for models that support it
            uploaded_url = await self._upload_ref_image(ref_images[0])
            if uploaded_url:
                params["image_url"] = uploaded_url

        async with httpx.AsyncClient(timeout=120) as client:
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

        image_url = data.get("images", [{}])[0].get("url", "")
        if not image_url:
            return ExecutorResult(content="No image returned", metadata=data)

        file_name = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(self.artifacts_dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        async with httpx.AsyncClient(timeout=60) as client:
            img_response = await client.get(image_url)
            img_response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(img_response.content)

        return ExecutorResult(
            content=prompt,
            file_paths=[file_path],
            metadata={"model": model, "fal_response": data},
        )

    async def _upload_ref_image(self, local_path: str) -> str | None:
        """Upload a local image file and return a public URL for it."""
        if not os.path.exists(local_path):
            return None
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Use fal.ai file upload
                with open(local_path, "rb") as f:
                    content_type = "image/png" if local_path.endswith(".png") else "image/jpeg"
                    response = await client.post(
                        "https://fal.ai/api/storage/upload",
                        headers={"Authorization": f"Key {self.api_key}"},
                        files={"file": (os.path.basename(local_path), f, content_type)},
                    )
                    if response.status_code == 200:
                        return response.json().get("url")
        except Exception:
            pass
        return None
