from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from typing import Callable, Mapping, Sequence

MIN_PYTHON_VERSION = (3, 10)
REQUIRED_PYTHON_RELATIVE = Path(".openclaw") / ".venv" / "bin" / "python3"


@dataclass(frozen=True)
class DoctorResult:
    ok: bool
    python_path: Path | None
    python_version: str | None
    errors: list[str]


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def _default_runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), check=True, capture_output=True, text=True)


def _parse_version_payload(raw_stdout: str) -> tuple[int, int, int]:
    payload = json.loads(raw_stdout.strip())
    major = int(payload["major"])
    minor = int(payload["minor"])
    micro = int(payload["micro"])
    return major, minor, micro


def run_doctor(
    *,
    env: Mapping[str, str] | None = None,
    run_command: CommandRunner | None = None,
) -> DoctorResult:
    runtime_env = os.environ if env is None else env
    runner = _default_runner if run_command is None else run_command

    home = runtime_env.get("HOME")
    if not home:
        return DoctorResult(
            ok=False,
            python_path=None,
            python_version=None,
            errors=["HOME environment variable is not set."],
        )

    python_path = Path(home) / REQUIRED_PYTHON_RELATIVE
    if not python_path.exists():
        return DoctorResult(
            ok=False,
            python_path=python_path,
            python_version=None,
            errors=[f"Required Python interpreter not found: {python_path}"],
        )

    if not os.access(python_path, os.X_OK):
        return DoctorResult(
            ok=False,
            python_path=python_path,
            python_version=None,
            errors=[f"Required Python interpreter is not executable: {python_path}"],
        )

    command = [
        str(python_path),
        "-c",
        (
            "import json, sys; "
            "print(json.dumps({'major': sys.version_info[0], "
            "'minor': sys.version_info[1], 'micro': sys.version_info[2]}))"
        ),
    ]

    try:
        completed = runner(command)
    except OSError as exc:
        return DoctorResult(
            ok=False,
            python_path=python_path,
            python_version=None,
            errors=[f"Failed to execute required Python interpreter: {exc}"],
        )
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or "").strip()
        suffix = f": {details}" if details else ""
        return DoctorResult(
            ok=False,
            python_path=python_path,
            python_version=None,
            errors=[
                "Required Python interpreter returned non-zero exit code"
                f"{suffix}"
            ],
        )

    try:
        major, minor, micro = _parse_version_payload(completed.stdout)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return DoctorResult(
            ok=False,
            python_path=python_path,
            python_version=None,
            errors=[f"Unable to parse Python version from doctor probe: {exc}"],
        )

    python_version = f"{major}.{minor}.{micro}"
    if (major, minor) < MIN_PYTHON_VERSION:
        return DoctorResult(
            ok=False,
            python_path=python_path,
            python_version=python_version,
            errors=[
                "Required Python interpreter version "
                f"{python_version} is below minimum 3.10."
            ],
        )

    return DoctorResult(
        ok=True,
        python_path=python_path,
        python_version=python_version,
        errors=[],
    )
