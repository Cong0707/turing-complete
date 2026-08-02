# Kind 95/96 位宽与 v15 保留审计

## 结论

- `get_output_word_size @ 0x1402367c6` 对 kind 95 的唯一输出使用 `VARIABLE_WIDTH`：显式组件 `word_size` 原样成为输出位宽；若组件宽度是 `AUTO_SIZE`，先替换为 `Bits(2)`，故有效输出宽度为 2。
- kind 96 有 1 个输入、0 个输出。它可以作为同组件宽度的输入 sink，但不存在合法的 output index；调用 `get_output_word_size(96, 0, ...)` 会命中输出数组边界错误。
- kind 95/96 在 `get_clamped_word_size @ 0x140236b33` 中共用 `0x140237379` 分支，普通显式宽度按 `clamp(width, 1, 2048)` 装板。
- 标签和 `settings` 不参与上述位宽计算；位宽由组件 `word_size` 与原型 pin 的 width descriptor 决定。
- raw v15 kind 95/96 会通过反序列化、原型查找和 `board_add_component`，后续保存仍写回原 kind 与钳制后的 `word_size`。这证明 raw 组件可保留，不等同于普通 UI 菜单可放置。

## 精确语义

```text
result = component_word_size
if result == AUTO_SIZE:
    result = Bits(2)

pin_width = PROTOTYPES[kind].outputs[output_index].word_size
if pin_width == VARIABLE_WIDTH:  result *= 1
if pin_width == VARIABLE_WIDTH2: result *= 2
if pin_width == VARIABLE_WIDTH4: result *= 4
if pin_width == VARIABLE_WIDTH8: result *= 8
otherwise:                       result = pin_width
```

当前二进制常量：

```text
AUTO_SIZE       = 0x8000000000000000
VARIABLE_WIDTH  = 0x7fffffffffffffff
VARIABLE_WIDTH2 = 0x7ffffffffffffffe
VARIABLE_WIDTH4 = 0x7ffffffffffffffd
VARIABLE_WIDTH8 = 0x7ffffffffffffffc
MAX_WIRE_WIDTH  = 2048
```

## v15 保留链

1. `get_component_v15` 接受 `kind <= 124`，因此 95/96 不会降为 kind 0。
2. `get_components_v15` 对每个解析出的组件直接 `result.add(comp)`，没有 95/96 白名单过滤。
3. `load_schematic_raw` 的主装板路径只排除 kind 0；custom kind 78 有独立校验，95/96 走原生 `PROTOTYPES`。
4. kind 95/96 原型均存在，`board_add_component` 保存其 kind 与钳制后的 `word_size`。
5. serializer 首先写 `component.kind`，并写 `word_size`；只有 custom kind 78 写额外尾字段。
6. `UNUSED_COMPONENTS` 不包含 `com_verilog_input` 或 `com_verilog_output`。

## 边界

本分支严格证明的是：kind 95 的位宽元数据可无额外普通元件地设为 1..2048、`AUTO_SIZE` 对应 2 位，以及 raw kind 95/96 可被 v15 加载和再保存。它尚未证明不同宽度在 Verilog codegen 中能提供可利用的任意 seed 位提取或免费截断；该判断必须与 `compiler_trace` 分支合并。

## 复验

```powershell
py -3 -m py_compile D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit\verilog_boundary\width_deserialize\verify_width_deserialize.py
py -3 D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit\verilog_boundary\width_deserialize\verify_width_deserialize.py
```

预期输出以 `PASS` 开头，并重建 `evidence.json`。验证目标 EXE：

```text
D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe
SHA-256 C93F5E8E826050C3F92E2B3891D26FCDFC933658614185CB9B2EB6A34C5B8D1C
```

整个复验只读当前 EXE、原型 JSON、恢复源码和反编译证据；不启动游戏，不读取或修改正式存档、`levels.txt`、`settings.txt` 或 token。
