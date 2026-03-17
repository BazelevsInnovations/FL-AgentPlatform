import asyncio
import os
import tempfile
import uuid

from fl_platform.executors.base import BaseExecutor, ExecutorResult


class PythonScriptExecutor(BaseExecutor):
    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = artifacts_dir

    async def execute(
        self,
        prompt: str,
        inputs: dict,
        *,
        model_id: str | None = None,
        system_prompt: str | None = None,
        extra_params: dict | None = None,
    ) -> ExecutorResult:
        script_code = prompt
        output_dir = os.path.join(self.artifacts_dir, uuid.uuid4().hex)
        os.makedirs(output_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            full_script = f'OUTPUT_DIR = "{output_dir}"\n'
            for key, value in inputs.items():
                if isinstance(value, str):
                    full_script += f'{key} = """{value}"""\n'
                else:
                    import json
                    full_script += f"import json\n{key} = json.loads('{json.dumps(value)}')\n"
            full_script += "\n" + script_code
            f.write(full_script)
            script_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=output_dir,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

            output_files = []
            for fname in os.listdir(output_dir):
                output_files.append(os.path.join(output_dir, fname))

            return ExecutorResult(
                content=stdout.decode() if stdout else "",
                file_paths=output_files,
                metadata={
                    "returncode": proc.returncode,
                    "stderr": stderr.decode() if stderr else "",
                },
            )
        finally:
            os.unlink(script_path)
