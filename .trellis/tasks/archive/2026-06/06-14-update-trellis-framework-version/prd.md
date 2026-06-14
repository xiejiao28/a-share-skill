# 升级 Trellis 框架版本

## 目标

将当前项目使用的 Trellis 从 0.5.19 升级到 0.6 RC 通道，并在本地项目中执行 Trellis 更新，使项目内的 Trellis 运行时、平台文件和模板进入 0.6 轨道。

## 已知信息

* 当前项目 `.trellis/.version` 为 `0.5.19`
* 当前本机 `trellis --version` 为 `0.5.19`
* npm `latest` 仍为 `0.5.19`
* npm `rc` 通道当前为 `0.6.0-rc.0`
* 用户明确要求直接升级替换，不先做额外评估

## 临时假设

* 本次升级包括全局 CLI 升级和项目内 `trellis update`
* 用户接受 Trellis 管理模板按 0.6 RC 直接覆盖更新
* 现有 `.trellis/tasks/`、`.trellis/spec/`、`.trellis/workspace/` 等用户数据按 Trellis 机制保留

## 开放问题

* 当前无阻塞问题，直接进入实现。

## 需求

* 升级全局 Trellis CLI 到 `@mindfoldhq/trellis@rc`
* 在项目内应用 Trellis 更新
* 验证本机 CLI 版本和项目版本记录

## 验收标准

* [ ] `trellis --version` 进入 `0.6` RC 通道
* [ ] 项目内 Trellis 更新完成
* [ ] 输出升级结果和剩余注意事项

## 明确不做

* 评估 0.6 全量功能差异
* 为 0.6 兼容性单独补代码
