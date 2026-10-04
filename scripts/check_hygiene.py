"""Check indexed content before a commit; never scan private sandbox files.

Credential-pattern matching is heuristic, not a guarantee of secret absence.
Only filenames and rule names are printed on failure, never matched secret values.
"""

import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PARTS = {
    "node_modules", ".next", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", ".pyright", "dist", "build", "coverage", "htmlcov",
    "artifacts", "uploads", "exports", "tmp", "temp", "media", "generated-assets",
    ".cache", ".config", ".local", ".omnirush", ".bun", ".npm", ".npm-cache",
}
BLOCKED_ROOT = {"package.json", "package-lock.json", ".bashrc", ".inputrc", ".bash_history"}
PATTERNS = {
    "absolute-home-path": re.compile(r"/home/[A-Za-z0-9_.-]+"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "provider-token": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
                                 r"github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b"),
    "credential-assignment": re.compile(
        r"(?im)^[ \t]*(?:[A-Z0-9_]*(?:API_KEY|SECRET|PASSWORD|TOKEN))[ \t]*=[ \t]*[^\s#]+"
    ),
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main() -> None:
    paths = [path.decode() for path in git("ls-files", "-z").split(b"\0") if path]
    if not paths:
        raise SystemExit("No indexed files: stage intended project content before this check.")
    failures = []
    size = 0
    for path in paths:
        parts = PurePosixPath(path).parts
        name = parts[-1]
        if (
            BLOCKED_PARTS.intersection(parts)
            or path in BLOCKED_ROOT
            or (name.startswith(".env") and name != ".env.example")
            or name.endswith((".pyc", ".pyo", ".tsbuildinfo", ".pem", ".key", ".log"))
        ):
            failures.append(f"{path}: forbidden artifact/environment path")
        content = git("show", f":{path}")
        size += len(content)
        if len(content) > 2_000_000:
            failures.append(f"{path}: large indexed asset (>2 MB)")
        if b"\0" in content:
            failures.append(f"{path}: binary content needs explicit review")
        text = content.decode("utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{path}: {label}")
        if name == ".env.example":
            for line in text.splitlines():
                if (
                    line.strip()
                    and not line.lstrip().startswith("#")
                    and not re.fullmatch(r"[A-Z][A-Z0-9_]*=", line)
                ):
                    failures.append(f"{path}: environment example must contain names only")
    print(f"Indexed/tracked files checked: {len(paths)}")
    print(f"Indexed content size: {size:,} bytes")
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("Environment/artifact/sandbox path checks: no matches")
    print("Credential-pattern scan: no matches (heuristic)")
    print("Machine-specific absolute home paths: no matches")
    print("Environment example: names only; no values")


if __name__ == "__main__":
    main()
