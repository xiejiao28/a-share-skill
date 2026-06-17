#!/usr/bin/env python3
"""Run fixed-parameter backtests across a stock pool and write a brief report."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import sys
import tempfile
from typing import Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
PAPER_TRADING_SCRIPTS = REPO_ROOT / "a-share-paper-trading" / "scripts"
if str(PAPER_TRADING_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PAPER_TRADING_SCRIPTS))

from paper_trading.engine import PaperTradingEngine  # noqa: E402
from paper_trading.market_data import MarketDataProvider  # noqa: E402


INITIAL_CASH = 100000.0
POOL = [
    {"symbol": "600517", "name": "国网英大"},
    {"symbol": "601669", "name": "中国电建"},
    {"symbol": "000060", "name": "中金岭南"},
    {"symbol": "002041", "name": "登海种业"},
    {"symbol": "002140", "name": "东华科技"},
    {"symbol": "002546", "name": "新联电子"},
    {"symbol": "603105", "name": "芯能科技"},
    {"symbol": "000630", "name": "铜陵有色"},
]
STRATEGIES = [
    {"strategy": "sma_cross", "params": {"fast": 30, "slow": 60}},
    {"strategy": "rsi_revert", "params": {"buy_rsi": 25.0, "sell_rsi": 60.0}},
]


@dataclass(frozen=True)
class RunConfig:
    start: str
    end: str
    initial_cash: float


def default_start_date() -> str:
    today = date.today()
    try:
        return today.replace(year=today.year - 1).isoformat()
    except ValueError:
        return today.replace(month=2, day=28, year=today.year - 1).isoformat()


def run_pool_backtests(config: RunConfig) -> Dict:
    provider = MarketDataProvider()
    rows: List[Dict] = []
    with tempfile.TemporaryDirectory() as tmp:
        engine = PaperTradingEngine(str(Path(tmp) / "stock_pool_best_params.db"), market_data=provider)
        for stock in POOL:
            for strategy in STRATEGIES:
                result = engine.run_backtest(
                    symbol=stock["symbol"],
                    strategy=strategy["strategy"],
                    start=config.start,
                    end=config.end,
                    initial_cash=config.initial_cash,
                    params=strategy["params"],
                )
                rows.append(
                    {
                        "strategy": strategy["strategy"],
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "start": config.start,
                        "end": config.end,
                        "params": strategy["params"],
                        "return_pct": float(result["total_return_pct"]),
                        "max_drawdown": float(result["max_drawdown_pct"]),
                        "final_equity": float(result["final_capital"]),
                        "trade_count": len(result["trades"]),
                    }
                )

    strategy_summary: List[Dict] = []
    for strategy in STRATEGIES:
        strategy_name = strategy["strategy"]
        subset = [row for row in rows if row["strategy"] == strategy_name]
        avg_return = round(sum(row["return_pct"] for row in subset) / len(subset), 2)
        avg_drawdown = round(sum(row["max_drawdown"] for row in subset) / len(subset), 2)
        positive_count = sum(1 for row in subset if row["return_pct"] > 0)
        strategy_summary.append(
            {
                "strategy": strategy_name,
                "params": strategy["params"],
                "average_return_pct": avg_return,
                "average_max_drawdown": avg_drawdown,
                "positive_count": positive_count,
                "stock_count": len(subset),
            }
        )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "start": config.start,
        "end": config.end,
        "initial_cash": config.initial_cash,
        "stock_pool": POOL,
        "strategies": STRATEGIES,
        "results": rows,
        "strategy_summary": strategy_summary,
    }


def build_output_paths(config: RunConfig) -> tuple[Path, Path]:
    stem = f"stock_pool_best_params_{config.start}_{config.end}"
    results_path = REPO_ROOT / "experiments" / "results" / f"{stem}.json"
    report_path = REPO_ROOT / "experiments" / "reports" / f"{stem}.md"
    return results_path, report_path


def write_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_report(payload: Dict) -> str:
    best_strategy = max(
        payload["strategy_summary"],
        key=lambda row: (row["average_return_pct"], -row["average_max_drawdown"]),
    )
    lines = [
        "# 股票池近一年策略对比结论",
        "",
        f"- 区间：`{payload['start']}` 到 `{payload['end']}`",
        f"- 股票数：`{len(payload['stock_pool'])}`",
        "",
        "## 结论",
        "",
        f"当前这组股票池里，整体更优的是 `{best_strategy['strategy']}`。",
        "",
        "| 策略 | 参数 | 平均收益率 | 平均最大回撤 | 正收益股票数 |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["strategy_summary"]:
        lines.append(
            f"| `{row['strategy']}` | `{row['params']}` | `{row['average_return_pct']}%` | "
            f"`{row['average_max_drawdown']}%` | `{row['positive_count']}/{row['stock_count']}` |"
        )
    lines.extend(["", "## 逐股票明细", ""])
    lines.append("| 股票 | `sma_cross` 收益 / 回撤 | `rsi_revert` 收益 / 回撤 |")
    lines.append("| --- | --- | --- |")
    by_symbol: Dict[str, Dict[str, Dict]] = {}
    for row in payload["results"]:
        by_symbol.setdefault(row["symbol"], {})[row["strategy"]] = row
    for stock in POOL:
        sma = by_symbol[stock["symbol"]]["sma_cross"]
        rsi = by_symbol[stock["symbol"]]["rsi_revert"]
        lines.append(
            f"| `{stock['symbol']}` {stock['name']} | `{sma['return_pct']}% / {sma['max_drawdown']}%` | "
            f"`{rsi['return_pct']}% / {rsi['max_drawdown']}%` |"
        )
    lines.extend(
        [
            "",
            "## 当前可用结论",
            "",
            "1. 这组股票池里可以直接比较两个已固定参数策略的迁移效果。",
            f"2. 当前整体更优的是 `{best_strategy['strategy']}`。",
            "3. 后续如果要继续推进，优先扩股票池而不是重新在这 8 只上调参。",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_report(payload) + "\n", encoding="utf-8")


def main() -> None:
    config = RunConfig(start=default_start_date(), end=date.today().isoformat(), initial_cash=INITIAL_CASH)
    payload = run_pool_backtests(config)
    results_path, report_path = build_output_paths(config)
    write_json(results_path, payload)
    write_report(report_path, payload)
    print(f"Wrote results to {results_path}")
    print(f"Wrote report to {report_path}")


if __name__ == "__main__":
    main()
