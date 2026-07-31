# Pareto 候选变体

## 2026-08-01 / 提交：功能：保存同一关卡的多条优化路径

单一 `candidate/circuit.data` 只能表示一个方案，但排行榜优化经常同时存在低门数、低延迟和
最低能耗等互不支配点。项目因此增加：

```text
examples/<level>/variants/<variant>/circuit.data
examples/<level>/variants/<variant>/metadata.json
```

构建全部已审查变体：

```powershell
.\.venv\Scripts\tc-save.exe build-variants
```

只构建指定关卡：

```powershell
.\.venv\Scripts\tc-save.exe build-variants signed_negator
```

命令只写项目目录，不读取或写入正式存档。每个变体与主候选使用同一套约束：保留固定端口、
严格 v15 往返、完整连通性检查、拒绝组合环，并穷举关卡输入真值表。`metadata.json` 记录文件
哈希、声明成本、结构规模和验证向量数，内容必须可重复生成。

首个变体为 `signed_negator/low-gate`：使用七级共享 OR 进位的 XOR 网络，达到
`21 gate / 8 delay / 168 energy`。现有 `24/5/120` 主候选继续保留，二者互不覆盖。
