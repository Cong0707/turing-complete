# Codex 自定义元件构建器

## 2026-08-01 / 提交：功能：建立 Codex 自定义元件构建与部署工具

### 身份与目录约定

Codex 自定义元件在项目中使用两种名称：

- `logical_key` 是不可变的 ASCII 身份键，例如 `foundry/codex/not_gate`。内部实现、中文显示名、
  门数和延迟发生变化时，该键不能变化。
- `display_path` 是用户在元件工坊看到的目录名，可以使用中文，例如 `非门`。

项目镜像和正式存档分别位于：

```text
examples/foundry/codex/<中文元件名>/candidate/circuit.data
%APPDATA%/Turing Complete/schematics/foundry/codex/<中文元件名>/circuit.data
```

`examples/foundry/codex/custom-ids.json` 是 Git 跟踪的身份注册表。`custom_id` 使用独立 SHA-256
域、项目命名空间、稳定逻辑键和显式 `nonce` 生成正 63 位整数。发生首次碰撞时只递增 nonce，
并把最终结果写入注册表；后续内部优化必须复用注册值，不能根据电路内容重新编号。

### 构建约束

`src/tc_save_lab/foundry.py` 在候选写入前执行以下检查：

- Custom 容器使用 v15、非零正数 `custom_id` 和精确 512 字节零值 `design`；
- `kind=79` 输入统一为现代三格接口和 `settings=(2,)`；
- `kind=81` 输出统一为现代三格接口和 `settings=(0,)`；
- 组件 `permanent_id` 必须为正且唯一；
- `dependencies` 必须严格等于 `kind=78` 实例按首次出现顺序去重后的 ID；
- 项目镜像和指定依赖根中的 `custom_id` 全局唯一，直接依赖完整且依赖图无环；
- 已注册元件的接口签名默认不可改变，避免破坏父级 Custom 实例。

构建命令接受一个 Circuit JSON 作为逻辑网络来源，忽略其中旧的 Custom 头部身份字段，并重建
受约束的 Foundry 容器：

```powershell
tc-save build-foundry not_gate 非门 .research/not_gate.json
```

引用正式 Foundry 中已有元件时，默认只读扫描当前存档以验证依赖和 ID 冲突；也可以通过
`--dependency-root` 指定另一个只读依赖根。接口确需变化时，必须显式使用
`--allow-interface-change`，并同步更新所有父级电路。

### 显式部署

部署不是构建过程的隐式副作用。以下命令只生成只读计划：

```powershell
tc-save deploy-foundry-codex --dry-run
```

正式部署必须再次显式执行，并确认目标：

```powershell
tc-save deploy-foundry-codex
```

部署器要求既有的 `schematics/foundry` 目录，拒绝路径逃逸、reparse point、大小写或 Unicode
路径碰撞、不同身份的原位覆盖、ID 冲突、缺失依赖、依赖环和计划后的文件变化。它会在开始和
目录切换前分别检查 `Turing Complete.exe`，进程检查失败时关闭写入路径。

写入使用同级临时目录完成全量反解析后再切换 `codex`。旧目录仅在事务期间临时存在；成功后
立即删除，不留下持久备份。失败时恢复原目录。未受项目注册表管理的既有 `codex` 元件会被
保留，不会因部署项目候选而删除。

### 离线验证

测试只使用 `TemporaryDirectory` 和进程检查 mock，不读取或写入正式存档，也不启动游戏。覆盖：

- 固定 `custom_id` 测试向量与 nonce；
- 三格输入输出端口；
- 首次出现有序依赖；
- 重复构建、内部更新和接口变化保护；
- 外部 ID 冲突；
- 部署保留未管理元件、状态漂移拒绝和无持久备份。
