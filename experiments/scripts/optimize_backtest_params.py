#!/usr/bin/env python3
"""Parameter sweep experiments for paper-trading backtests."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import sys
import tempfile
from typing import Dict, Iterable, List


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
PAPER_TRADING_SCRIPTS = REPO_ROOT / "a-share-paper-trading" / "scripts"
if str(PAPER_TRADING_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PAPER_TRADING_SCRIPTS))

from paper_trading.engine import PaperTradingEngine  # noqa: E402
from paper_trading.market_data import MarketDataProvider  # noqa: E402


DEFAULT_SYMBOL = "601669"
DEFAULT_INITIAL_CASH = 100000.0
DEFAULT_SMA_FAST = [3, 5, 8, 10, 12, 15]
DEFAULT_SMA_SLOW = [20, 30, 40, 60]
DEFAULT_RSI_BUY = [20.0, 25.0, 30.0, 35.0]
DEFAULT_RSI_SELL = [60.0, 65.0, 70.0, 75.0, 80.0]


@dataclass(frozen=True)
class ExperimentConfig:
    strategy: str
    symbol: str
    start: str
    end: str
    initial_cash: float
    fast_values: tuple[int, ...]
    slow_values: tuple[int, ...]
    buy_rsi_values: tuple[float, ...]
    sell_rsi_values: tuple[float, ...]


def _default_start_date() -> str:
    today = date.today()
    try:
        return today.replace(year=today.year - 3).isoformat()
    except ValueError:
        # Feb 29 fallback.
        return today.replace(month=2, day=28, year=today.year - 3).isoformat()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run parameter sweep experiments on paper-trading backtests.")
    parser.add_argument("--strategy", default="sma_cross", choices=["sma_cross", "rsi_revert"])
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--start", default=_default_start_date())
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--cash", type=float, default=DEFAULT_INITIAL_CASH)
    parser.add_argument("--fast-values", help="Comma-separated SMA fast-window candidates, e.g. 3,5,8,10,12,15")
    parser.add_argument("--slow-values", help="Comma-separated SMA slow-window candidates, e.g. 20,30,40,60")
    parser.add_argument("--buy-rsi-values", help="Comma-separated RSI buy-threshold candidates, e.g. 20,25,30,35")
    parser.add_argument("--sell-rsi-values", help="Comma-separated RSI sell-threshold candidates, e.g. 60,65,70,75,80")
    parser.add_argument("--output", help="Optional explicit output path for the JSON result file.")
    return parser


def parse_int_list(raw: str | None, default: List[int], arg_name: str) -> tuple[int, ...]:
    if not raw:
        return tuple(default)
    values: List[int] = []
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item:
            continue
        value = int(item)
        if value <= 0:
            raise ValueError(f"{arg_name} must contain positive integers")
        values.append(value)
    if not values:
        raise ValueError(f"{arg_name} cannot be empty")
    return tuple(sorted(set(values)))


def parse_float_list(raw: str | None, default: List[float], arg_name: str) -> tuple[float, ...]:
    if not raw:
        return tuple(default)
    values: List[float] = []
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item:
            continue
        value = float(item)
        if value <= 0:
            raise ValueError(f"{arg_name} must contain positive numbers")
        values.append(value)
    if not values:
        raise ValueError(f"{arg_name} cannot be empty")
    return tuple(sorted(set(values)))


def generate_sma_cross_grid(fast_values: Iterable[int], slow_values: Iterable[int]) -> List[Dict[str, int]]:
    grid: List[Dict[str, int]] = []
    for fast in fast_values:
        for slow in slow_values:
            if fast < slow:
                grid.append({"fast": fast, "slow": slow})
    return grid


def generate_rsi_revert_grid(buy_candidates: Iterable[float], sell_candidates: Iterable[float]) -> List[Dict[str, float]]:
    grid: List[Dict[str, float]] = []
    for buy_rsi in buy_candidates:
        for sell_rsi in sell_candidates:
            if buy_rsi < sell_rsi:
                grid.append({"buy_rsi": buy_rsi, "sell_rsi": sell_rsi})
    return grid


def generate_grid(strategy: str) -> List[Dict[str, float]]:
    if strategy == "sma_cross":
        raise ValueError("sma_cross grid requires config-aware generation")
    if strategy == "rsi_revert":
        raise ValueError("rsi_revert grid requires config-aware generation")
    raise ValueError(f"unsupported strategy: {strategy}")


def compute_return_drawdown_ratio(return_pct: float, max_drawdown: float) -> float | None:
    if max_drawdown <= 0:
        if return_pct > 0:
            return None
        return 0.0
    return round(return_pct / max_drawdown, 4)


def sort_results(rows: Iterable[Dict]) -> List[Dict]:
    def sort_key(row: Dict) -> tuple:
        ratio = row["return_drawdown_ratio"]
        ratio_value = float("inf") if ratio is None and row["return_pct"] > 0 else float(ratio or 0.0)
        return (
            ratio_value,
            float(row["return_pct"]),
            -float(row["max_drawdown"]),
            -int(row["trade_count"]),
        )

    sorted_rows = sorted(rows, key=sort_key, reverse=True)
    for rank, row in enumerate(sorted_rows, start=1):
        row["rank"] = rank
    return sorted_rows


def run_experiment(config: ExperimentConfig) -> Dict:
    if config.strategy == "sma_cross":
        grid = generate_sma_cross_grid(config.fast_values, config.slow_values)
    elif config.strategy == "rsi_revert":
        grid = generate_rsi_revert_grid(config.buy_rsi_values, config.sell_rsi_values)
    else:
        grid = generate_grid(config.strategy)
    if not grid:
        raise ValueError("parameter grid is empty after applying constraints")
    provider = MarketDataProvider()

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / f"{config.strategy}_{config.symbol}.db"
        engine = PaperTradingEngine(str(db_path), market_data=provider)

        rows: List[Dict] = []
        for params in grid:
            result = engine.run_backtest(
                symbol=config.symbol,
                strategy=config.strategy,
                start=config.start,
                end=config.end,
                initial_cash=config.initial_cash,
                params=params,
            )
            return_pct = float(result["total_return_pct"])
            max_drawdown = float(result["max_drawdown_pct"])
            row = {
                "strategy": config.strategy,
                "symbol": result["symbol"],
                "start": config.start,
                "end": config.end,
                "params": params,
                "final_equity": float(result["final_capital"]),
                "return_pct": return_pct,
                "max_drawdown": max_drawdown,
                "return_drawdown_ratio": compute_return_drawdown_ratio(return_pct, max_drawdown),
                "trade_count": len(result["trades"]),
                "rank": 0,
            }
            rows.append(row)

    ranked_rows = sort_results(rows)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "strategy": config.strategy,
        "symbol": config.symbol,
        "start": config.start,
        "end": config.end,
        "initial_cash": config.initial_cash,
        "grid_params": {
            "fast_values": list(config.fast_values) if config.strategy == "sma_cross" else None,
            "slow_values": list(config.slow_values) if config.strategy == "sma_cross" else None,
            "buy_rsi_values": list(config.buy_rsi_values) if config.strategy == "rsi_revert" else None,
            "sell_rsi_values": list(config.sell_rsi_values) if config.strategy == "rsi_revert" else None,
        },
        "grid_size": len(grid),
        "results": ranked_rows,
    }


def build_output_path(config: ExperimentConfig, explicit_output: str | None) -> Path:
    if explicit_output:
        return Path(explicit_output)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{config.strategy}_{config.symbol}_{config.start}_{config.end}_{timestamp}.json"
    return REPO_ROOT / "experiments" / "results" / filename


def write_result(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def print_summary(payload: Dict, output_path: Path) -> None:
    print(f"Wrote {payload['grid_size']} results to {output_path}")
    for row in payload["results"][:5]:
        print(
            f"#{row['rank']} params={row['params']} return={row['return_pct']}% "
            f"drawdown={row['max_drawdown']}% ratio={row['return_drawdown_ratio']} trades={row['trade_count']}"
        )


def main() -> None:
    args = build_parser().parse_args()
    if args.cash <= 0:
        raise ValueError("cash must be positive")
    fast_values = parse_int_list(args.fast_values, DEFAULT_SMA_FAST, "--fast-values")
    slow_values = parse_int_list(args.slow_values, DEFAULT_SMA_SLOW, "--slow-values")
    buy_rsi_values = parse_float_list(args.buy_rsi_values, DEFAULT_RSI_BUY, "--buy-rsi-values")
    sell_rsi_values = parse_float_list(args.sell_rsi_values, DEFAULT_RSI_SELL, "--sell-rsi-values")
    config = ExperimentConfig(
        strategy=args.strategy,
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        initial_cash=args.cash,
        fast_values=fast_values,
        slow_values=slow_values,
        buy_rsi_values=buy_rsi_values,
        sell_rsi_values=sell_rsi_values,
    )
    payload = run_experiment(config)
    output_path = build_output_path(config, args.output)
    write_result(output_path, payload)
    print_summary(payload, output_path)


if __name__ == "__main__":
    main()
