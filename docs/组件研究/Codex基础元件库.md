# Codex 基础元件库

## 2026-08-01 / 提交：功能：生成首批Codex基础元件

`src/tc_save_lab/codex_library.py` 保存经过人工审查的现代 Foundry 元件配方。运行：

```powershell
.\.venv\Scripts\tc-foundry.exe build-known
```

只会在项目的 `examples/foundry/codex` 中生成候选、元数据和稳定 ID 注册记录，不会部署
正式存档。当前首批包括：

| 元件 | gate | delay | energy | 穷举向量 |
| --- | ---: | ---: | ---: | ---: |
| 半加器/低门数 | 3 | 2 | 6 | 4 |
| 全加器/低门数 | 7 | 4 | 28 | 8 |

每个配方必须同时通过：现代三格 Foundry 接口检查、v15 往返、端点连通性、多输出完整真值
表和稳定 `custom_id` 注册。旧 `OVERTRUE`、`LEG` 和完整 `Overture` 架构不作为配方来源，
只保留为历史文件解析样本。
