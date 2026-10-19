"""Reject oversized publication files before artifact upload and Git commit."""

import argparse
from pathlib import Path
import subprocess

MAX_FILE_BYTES = 50 * 1024 * 1024


def staged_sizes():
    names = subprocess.check_output(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z"])
    for name in names.decode("utf-8").split("\0"):
        if name:
            size = subprocess.check_output(["git", "cat-file", "-s", f":{name}"])
            yield name, int(size)


def directory_sizes(root):
    if not root.is_dir():
        raise ValueError(f"Publication directory does not exist: {root}")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Publication must not contain symlinks: {path}")
        if path.is_file():
            yield str(path.relative_to(root)), path.stat().st_size


def validate(sizes, limit=MAX_FILE_BYTES):
    oversized = [(name, size) for name, size in sizes if size > limit]
    if oversized:
        detail = "; ".join(f"{name}: {size:,} bytes" for name, size in oversized)
        raise ValueError(f"Publication blocked before commit: files exceed {limit:,} bytes: {detail}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--root", type=Path)
    mode.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    try:
        validate(staged_sizes() if args.staged else directory_sizes(args.root))
    except ValueError as error:
        parser.exit(1, str(error) + "\n")
    print("Publication file sizes are within the 50 MiB budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
