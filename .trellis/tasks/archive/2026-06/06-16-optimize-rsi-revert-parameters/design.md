# rsi_revert 参数调优设计

## 范围

本子任务只负责：

- `rsi_revert` 策略
- 单票 `601669`
- 近 3 年区间

依赖前提：

- `sma_cross` 子任务已先完成，用来跑通统一实验骨架

## 设计目标

在已验证过的实验骨架上，补上 `rsi_revert` 的参数空间与结果输出，使两个策略可在同一评价口径下比较。

## 参数空间

当前参数：

- `buy_rsi`
- `sell_rsi`

基本约束：

- `buy_rsi < sell_rsi`

实现时还应避免：

- 阈值过近导致频繁翻转
- 买入阈值过高或卖出阈值过低导致策略语义失真

## 设计原则

### 1. 复用 `sma_cross` 阶段沉淀的实验骨架

本任务不应重新发明文件结构、排序器和输出格式。

### 2. 只替换参数空间与策略名

理想状态下：

- 实验脚本框架不变
- 只新增 `rsi_revert` 的参数枚举和约束

### 3. 保持策略对比可比性

结果字段、排序方式、文件格式都应与 `sma_cross` 子任务一致。

## 结果契约

沿用父任务统一字段：

- `strategy`
- `symbol`
- `start`
- `end`
- `params`
- `final_equity`
- `return_pct`
- `max_drawdown`
- `return_drawdown_ratio`
- `trade_count`
- `rank`

## 文件输出

结果文件放在：

- `experiments/results/`

建议命名：

- `rsi_revert_601669_<range>_<timestamp>.json`

## 风险

### 风险 1：参数空间和策略语义脱节

应对：

- 保持 `buy_rsi < sell_rsi`
- 避免不合理阈值组合进入最终排序

### 风险 2：输出格式和 `sma_cross` 分叉

应对：

- 强制复用同一结果契约
