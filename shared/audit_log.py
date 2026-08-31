"""Log di audit append-only per ogni azione (lettura e scrittura) eseguita
dai server MCP. Un file JSONL per piattaforma in /logs."""
import json
import time
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def log_action(platform: str, tool: str, params: dict, result: dict, dry_run: bool) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "platform": platform,
        "tool": tool,
        "dry_run": dry_run,
        "params": params,
        "result": result,
    }
    path = LOG_DIR / f"{platform}_audit.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
