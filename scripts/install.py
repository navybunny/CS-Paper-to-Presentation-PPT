"""Install only the public skill folder, without overwriting an existing skill.

SPDX-License-Identifier: MIT
"""
import argparse
import os
from pathlib import Path
import shutil
import sys

NAME = "cs-paper-to-presentation-ppt"


def default_destination():
    configured = os.environ.get("CODEX_HOME")
    codex_dir = Path(configured).expanduser() if configured else Path.home() / ".codex"
    return codex_dir / "skills"


def install(destination):
    source = Path(__file__).resolve().parent.parent / "skills" / NAME
    if not (source / "SKILL.md").is_file():
        raise ValueError("The source skill is missing SKILL.md; run this script from the repository download.")
    destination = Path(destination).expanduser().resolve()
    target = destination / NAME
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing to overwrite an existing skill: {target}")
    if target == source or source in target.parents:
        raise ValueError("Choose an installation destination outside the source skill.")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("Unexpected symlink in source skill; inspect the package before installing.")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=None, help="Skills parent directory (default: CODEX_HOME/skills or ~/.codex/skills)")
    args = parser.parse_args()
    try:
        target = install(args.dest if args.dest is not None else default_destination())
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation failed: {error}\n")
    print(f"Installed {NAME} to {target}")
    print("Use $cs-paper-to-presentation-ppt in your next turn. If needed, reload skills in your host.")


if __name__ == "__main__":
    main()
