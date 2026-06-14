# 增加 experiments 实验工作区

## 目标

在仓库根目录新增 `experiments/` 实验工作区，为策略研究提供统一的脚本目录、实验结果目录和实验报告目录。

## 已知信息

* 用户要求在仓库根目录新增 `experiments/`。
* `experiments/` 下需要包含三个子目录：`scripts/`、`results/`、`reports/`。
* 目录用途已经明确：
* `scripts/` 用于编写实验脚本。
* `results/` 用于保存实验结果。
* `reports/` 用于保存实验报告。
* 仓库当前还没有 `experiments/` 目录。
* 当前 `.gitignore` 只忽略了 `a-share-data/cache/` 和 `a-share-paper-trading/cache/`。
* 用户已明确：`experiments/results/` 下的内容也提交到 git，不做默认忽略。

## 临时假设

* 本任务只负责搭建实验目录骨架，并在需要时添加用于保留空目录的占位文件。
* 本任务不包含具体回测脚本、参数搜索脚本或实验报告模板的实现。
* `results/` 目录默认纳入版本管理，后续由用户自行控制结果文件大小和提交范围。

## 开放问题

* 当前无阻塞性开放问题，需求已足够进入实现。

## 需求

* 在仓库根目录新增 `experiments/`。
* 新增 `experiments/scripts/`。
* 新增 `experiments/results/`。
* 新增 `experiments/reports/`。
* 目录结构需要显式纳入 git 管理，避免空目录在仓库中丢失。

## 验收标准

* [ ] 仓库根目录存在 `experiments/scripts/`、`experiments/results/`、`experiments/reports/`。
* [ ] 空目录通过仓库约定的占位方式稳定保留在 git 中。
* [ ] `experiments/results/` 不被 `.gitignore` 默认忽略。

## 完成定义

* 在适用时补充或更新测试
* lint / typecheck / CI 通过
* 若行为变化涉及文档，则同步更新说明
* 评估回滚成本和风险

## 明确不做

* 实现具体回测脚本
* 实现参数搜索或参数优化逻辑
* 产出实验结果或实验报告内容

## 技术备注

* 仓库检查结果：
* `README.md` 目前描述了数据、策略和模拟盘能力，但没有实验工作区约定。
* `.gitignore` 当前非常精简，没有针对 `experiments/` 的规则。
* 当前任务路径：`.trellis/tasks/06-14-add-experiments-workspace-for-strategy-research/`
