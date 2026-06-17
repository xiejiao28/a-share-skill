#!/usr/bin/env python3
"""Maintain account state logs, action logs, and manual review logs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
PAPER_TRADING_SCRIPTS = REPO_ROOT / "a-share-paper-trading" / "scripts"
if str(PAPER_TRADING_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PAPER_TRADING_SCRIPTS))

from paper_trade_cli import request_json  # noqa: E402
from paper_trading_runtime import DEFAULT_HOST, DEFAULT_PORT  # noqa: E402


LOG_ROOT = REPO_ROOT / "log"
ACCOUNT_DIR = LOG_ROOT / "account"
ACTION_DIR = LOG_ROOT / "actions"
REVIEW_DIR = LOG_ROOT / "reviews"
BASE_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


@dataclass(frozen=True)
class LogPaths:
    account: Path
    actions: Path
    reviews: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain account state logs and manual review records.")
    parser.add_argument("--base-url", default=BASE_URL)
    sub = parser.add_subparsers(dest="command", required=True)

    account = sub.add_parser("record-account")
    account.add_argument("--account-id", required=True)
    account.add_argument("--source", choices=["manual", "paper_trading"], default="manual")
    account.add_argument("--total-asset", type=float)
    account.add_argument("--available-cash", type=float)
    account.add_argument("--position-ratio", type=float)
    account.add_argument("--holdings-file", help="Optional markdown or text file containing current holdings lines.")
    account.add_argument("--note", default="")

    action = sub.add_parser("record-action")
    action.add_argument("--account-id", required=True)
    action.add_argument("--action", required=True, help="e.g. buy/sell/add/reduce/clear")
    action.add_argument("--symbol", required=True)
    action.add_argument("--name", default="")
    action.add_argument("--qty", type=int)
    action.add_argument("--price", type=float)
    action.add_argument("--reason", required=True)
    action.add_argument("--note", default="")

    review = sub.add_parser("review")
    review.add_argument("--account-id", required=True)
    review.add_argument("--source", choices=["manual", "paper_trading"], default="paper_trading")
    review.add_argument("--holdings-file", help="Manual source only: optional holdings file")
    review.add_argument("--total-asset", type=float)
    review.add_argument("--available-cash", type=float)
    review.add_argument("--position-ratio", type=float)
    review.add_argument("--note", default="")
    return parser


def ensure_dirs() -> LogPaths:
    ACCOUNT_DIR.mkdir(parents=True, exist_ok=True)
    ACTION_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    return LogPaths(account=ACCOUNT_DIR, actions=ACTION_DIR, reviews=REVIEW_DIR)


def now_stamp() -> tuple[str, str]:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d_%H%M%S_%f")


def latest_markdown(path: Path) -> Optional[Path]:
    files = sorted(path.glob("*.md"))
    return files[-1] if files else None


def parse_section(text: str, title: str) -> List[str]:
    pattern = rf"## {re.escape(title)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, text, re.S)
    if not match:
        return []
    body = match.group(1).strip()
    if not body:
        return []
    return [line.rstrip() for line in body.splitlines()]


def read_holdings_lines(path: Optional[str]) -> List[str]:
    if not path:
        return []
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"holdings file not found: {path}")
    return [line.rstrip() for line in file_path.read_text(encoding="utf-8").splitlines()]


def fetch_paper_trading_snapshot(base_url: str, account_id: str) -> Dict:
    result = request_json(base_url.rstrip("/"), "GET", f"/accounts/{account_id}")
    if result.get("status") != "success":
        raise RuntimeError(result.get("message") or "failed to fetch account")
    return result["data"]


def build_manual_account_snapshot(args: argparse.Namespace) -> Dict:
    holdings = read_holdings_lines(args.holdings_file)
    return {
        "account_id": args.account_id,
        "source": "manual",
        "total_asset": args.total_asset,
        "available_cash": args.available_cash,
        "position_ratio": args.position_ratio,
        "holdings_lines": holdings,
        "note": args.note,
    }


def build_live_account_snapshot(base_url: str, account_id: str, note: str) -> Dict:
    account = fetch_paper_trading_snapshot(base_url, account_id)
    holdings_lines = [
        f"- {item['symbol']} qty={item['qty']} sellable={item['sellable_qty']} "
        f"avg_cost={item['avg_cost']} last_price={item['last_price']} "
        f"market_value={item['market_value']} unrealized_pnl={item['unrealized_pnl']}"
        for item in account["positions"]
    ]
    position_ratio = round(account["market_value"] / account["net_asset"] * 100, 2) if account["net_asset"] else 0.0
    return {
        "account_id": account_id,
        "source": "paper_trading",
        "total_asset": account["net_asset"],
        "available_cash": account["available_cash"],
        "position_ratio": position_ratio,
        "holdings_lines": holdings_lines,
        "note": note,
        "raw_account": account,
    }


def write_account_record(snapshot: Dict) -> Path:
    display_time, stamp = now_stamp()
    path = ACCOUNT_DIR / f"{stamp}_account.md"
    lines = [
        "# 账户状态记录",
        "",
        f"- 时间：`{display_time}`",
        f"- 账户：`{snapshot['account_id']}`",
        f"- 来源：`{snapshot['source']}`",
        f"- 总资产：`{snapshot['total_asset']}`",
        f"- 可用现金：`{snapshot['available_cash']}`",
        f"- 当前仓位：`{snapshot['position_ratio']}`",
        "",
        "## 持仓",
    ]
    lines.extend(snapshot["holdings_lines"] or ["- (空)"])
    lines.extend(["", "## 备注", snapshot.get("note", "") or "-"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_action_record(args: argparse.Namespace) -> Path:
    display_time, stamp = now_stamp()
    path = ACTION_DIR / f"{stamp}_action.md"
    lines = [
        "# 操作记录",
        "",
        f"- 时间：`{display_time}`",
        f"- 账户：`{args.account_id}`",
        f"- 操作：`{args.action}`",
        f"- 股票：`{args.symbol}` {args.name}".rstrip(),
        f"- 数量：`{args.qty}`" if args.qty is not None else "- 数量：`未提供`",
        f"- 价格：`{args.price}`" if args.price is not None else "- 价格：`未提供`",
        "",
        "## 原因",
        args.reason,
        "",
        "## 备注",
        args.note or "-",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def extract_review_timestamp(path: Path) -> Optional[str]:
    match = re.match(r"(\d{4}-\d{2}-\d{2}_\d{6}_\d{6})_review\.md$", path.name)
    return match.group(1) if match else None


def collect_actions_since(last_review: Optional[Path]) -> List[Path]:
    actions = sorted(ACTION_DIR.glob("*.md"))
    if not last_review:
        return actions
    cutoff = extract_review_timestamp(last_review)
    if not cutoff:
        return actions
    return [path for path in actions if path.name[:17] > cutoff]


def build_review_record(base_url: str, args: argparse.Namespace) -> Path:
    last_review = latest_markdown(REVIEW_DIR)
    latest_account = latest_markdown(ACCOUNT_DIR)
    if args.source == "paper_trading":
        snapshot = build_live_account_snapshot(base_url, args.account_id, args.note)
    else:
        snapshot = build_manual_account_snapshot(args)

    account_path = write_account_record(snapshot)
    actions = collect_actions_since(last_review)
    previous_review_text = last_review.read_text(encoding="utf-8") if last_review else ""
    previous_account_text = latest_account.read_text(encoding="utf-8") if latest_account else ""

    advice = []
    position_ratio = snapshot["position_ratio"] or 0
    if position_ratio >= 80:
        advice.append("当前仓位偏高，优先审查弱势持仓，避免继续被动加仓。")
    elif position_ratio <= 30:
        advice.append("当前仓位较低，可重点等待更清晰的入场信号，而不是急于补仓。")
    else:
        advice.append("当前仓位处于中间区域，建议把关注点放在持仓质量而不是单纯仓位高低。")
    if actions:
        advice.append("本次复盘已纳入上次复盘后的新增操作，请重点核对这些操作是否符合原始计划。")
    else:
        advice.append("上次复盘后没有新增操作记录，建议确认是否有遗漏补录。")

    display_time, stamp = now_stamp()
    path = REVIEW_DIR / f"{stamp}_review.md"
    lines = [
        "# 复盘记录",
        "",
        f"- 时间：`{display_time}`",
        f"- 账户：`{args.account_id}`",
        f"- 当前账户快照：`{account_path.name}`",
        f"- 上次复盘：`{last_review.name}`" if last_review else "- 上次复盘：`无`",
        "",
        "## 两次复盘之间的变化",
        f"- 新增操作记录数：`{len(actions)}`",
        f"- 最新账户来源：`{snapshot['source']}`",
        f"- 当前总资产：`{snapshot['total_asset']}`",
        f"- 当前可用现金：`{snapshot['available_cash']}`",
        f"- 当前仓位：`{snapshot['position_ratio']}`",
        "",
        "## 新增操作记录",
    ]
    if actions:
        lines.extend([f"- {action.name}" for action in actions])
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## 当前持仓摘要",
        ]
    )
    lines.extend(snapshot["holdings_lines"] or ["- (空)"])
    lines.extend(
        [
            "",
            "## 上次复盘参考",
            previous_review_text if previous_review_text else "- 无",
            "",
            "## 上次账户状态参考",
            previous_account_text if previous_account_text else "- 无",
            "",
            "## 建议",
        ]
    )
    lines.extend([f"- {item}" for item in advice])
    if args.note:
        lines.extend(["", "## 备注", args.note])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    ensure_dirs()
    args = build_parser().parse_args()
    base_url = args.base_url.rstrip("/")
    if args.command == "record-account":
        if args.source == "manual":
            snapshot = build_manual_account_snapshot(args)
        else:
            snapshot = build_live_account_snapshot(base_url, args.account_id, args.note)
        path = write_account_record(snapshot)
        print(f"Wrote account log to {path}")
        return
    if args.command == "record-action":
        path = write_action_record(args)
        print(f"Wrote action log to {path}")
        return
    if args.command == "review":
        path = build_review_record(base_url, args)
        print(f"Wrote review log to {path}")
        return
    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    main()
