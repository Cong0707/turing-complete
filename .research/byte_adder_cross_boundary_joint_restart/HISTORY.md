# History

## 2026-08-04 07:35 CST

- 完整封闭 `g16/n14/C5=multi_d2/T5=1/S5=1` 的 13 个 C5 祖先正常形 shard：`multi_d2_k0..k12`。
- 终态为 `13 UNSAT / 0 SAT / 0 UNKNOWN`；每片均为 `cadical195` 正常退出并通过 constraint、dependency、transport 和 wrapper 独立审计。
- 聚合覆盖审计：`bit35_joint_g16_n14_c5_multi_d2_t1_s1_complete_audit.json`，SHA-256 `e803d21011b30bf9dea2a9d267480ce1ed93992c60829de7a66f8de6b04a7fa1`。
- artifact collection SHA-256：`e43bd4255055058b3b5b21ec92fc70b26274a914e22d1103d8ca6c3374c21249`。
- 新增中文报告：`2026-08-04-bit35-n14-multi-d2-完整封闭.md`。
- SAT 接受链已用 g17 证书正回归：完整 `80/7/560`、`131072` 行、mismatch/conflict/output-Z 全零；独立 full-DAG verifier 结果 SHA-256 `27622d0894cc552e656f76b76ab65b67306748548190237e7a5cad1a9f4af8bc`。
- 下一组单 worker 优先级：`g16/n13/C5=multi_d2/T5=1/S5=1`，顺序 `k3,k2,k4,k1,k5,k0,k6,k7,k8,k9,k10,k11`。
- 本次封闭材料的逐文件 SHA-256 清单：`bit35_joint_g16_n14_multi_d2_SHA256SUMS.txt`；使用相对路径、按路径排序，且 manifest 不包含自身。
- 操作边界保持：未启动游戏，未读取正式存档，未修改/部署 candidate，未执行 Git add/commit。
