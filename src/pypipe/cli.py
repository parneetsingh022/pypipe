import os
import re
import stat
import runpy
from pathlib import Path
from pypipe.transpilers.github import GitHubTranspiler
from pypipe import registry

# Match variations like:
# "# pypipe: keep", "#pypipe: keep", "#pypipe : keep", any spacing/case
KEEP_REGEX = re.compile(r'^\s*#\s*pypipe\s*:\s*keep\s*$', re.IGNORECASE)

def _get_pipelines_dict():
    if hasattr(registry, "_pipelines") and isinstance(registry._pipelines, dict):
        return registry._pipelines
    raise RuntimeError("No _pipelines found in pypipe.registry")

def _has_keep_marker(path: Path, max_lines: int = 10) -> bool:
    """Return True if the file contains a keep marker in the first few lines."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                if KEEP_REGEX.match(line.strip()):
                    return True
    except Exception:
        # unreadable -> treat as not marked (eligible for deletion)
        return False
    return False

def _safe_unlink(path: Path) -> bool:
    """Try to delete a file robustly across OSes; return True if removed."""
    try:
        path.unlink()
        return True
    except PermissionError:
        # Try to relax permissions and retry (helps on Windows)
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)  # owner read/write
            path.unlink()
            return True
        except Exception:
            return False
    except FileNotFoundError:
        return True
    except Exception:
        return False

def _clean_orphaned(out_dir: Path, valid_names: set[str]) -> None:
    """Remove .yml files not in valid_names unless they have the keep marker."""
    for f in out_dir.glob("*.yml"):
        if f.stem in valid_names:
            continue
        if _has_keep_marker(f):
            print(f"[PyPipe] Keeping {f} (keep marker found)")
            continue
        if _safe_unlink(f):
            print(f"\033[91m[PyPipe] Removed {f} (not in registry)\033[0m")
        else:
            # Don’t fail the run—just warn
            print(f"\033[93m[PyPipe] Warning: could not remove {f} (permissions?)\033[0m")



def cmd_build(src_dir: str = ".pipe", out_dir: str = ".github/workflows", clean: bool = False) -> int:
    SRC_DIR = Path(src_dir)
    OUT_DIR = Path(out_dir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(SRC_DIR.glob("pipeline_*.py")) + sorted(SRC_DIR.glob("*_pipeline.py"))
    print(f"[PyPipe] Found {len(files)} pipeline files:")
    for f in files:
        print(f"[PyPipe] Running {f}...")
        runpy.run_path(str(f))

    pipelines = _get_pipelines_dict()
    if not pipelines:
        print("[PyPipe] No pipelines registered.")
        return 0

    for name, pipe in pipelines.items():
        out_path = OUT_DIR / f"{name}.yml"
        out_path.write_text(GitHubTranspiler(pipe).to_yaml())
        print(f"[PyPipe] Wrote {out_path}")

    if clean:
        _clean_orphaned(OUT_DIR, set(pipelines.keys()))

    print(f"\n✨ Done. {len(pipelines)} workflows written.")
    return 0

def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="pypipe", description="PyPipe CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Generate GitHub Actions workflows")
    p_build.add_argument("--src-dir", default=".pipe", help="Where pipeline_*.py live")
    p_build.add_argument("--out-dir", default=".github/workflows", help="Where to write .yml")
    p_build.add_argument("--clean", action="store_true", help="Remove old workflow files not in registry (respects keep marker)")

    args = parser.parse_args(argv)
    if args.command == "build":
        return cmd_build(args.src_dir, args.out_dir, args.clean)
    return 0
