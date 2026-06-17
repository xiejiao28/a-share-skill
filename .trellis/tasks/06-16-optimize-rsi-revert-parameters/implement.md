# rsi_revert 参数调优实施计划

## 实施目标

在 `sma_cross` 子任务已经验证过实验骨架的前提下，补上 `rsi_revert` 单票参数调优结果。

## 步骤

### 1. 确认 `rsi_revert` 回测输入

- 阅读 `run_backtest(...)`
- 确认 `buy_rsi` / `sell_rsi` 参数键
- 确认结果中可直接复用的字段

### 2. 定义参数网格

- 生成 `buy_rsi` / `sell_rsi` 参数组合
- 应用 `buy_rsi < sell_rsi` 约束

### 3. 复用实验骨架执行回测

- 沿用前一个子任务验证过的实验编排方式
- 逐组调用 `run_backtest(...)`

### 4. 统一补算指标与排序

- 总收益率
- 最大回撤
- 收益回撤比
- 交易次数

### 5. 落盘结果

- 输出到 `experiments/results/`
- 文件结构和 `sma_cross` 子任务保持一致

## 验证

- 至少成功跑出一份 `rsi_revert` 结果文件
- 抽查前几组参数，确认 `buy_rsi < sell_rsi`
- 与 `sma_cross` 的结果字段保持一致

## 回滚点

- 如果 `rsi_revert` 结果输出与前一子任务分叉，先回退到统一骨架
- 如果参数空间过大导致验证过慢，先缩小网格再验证
