# EABI 兼容改造上下文记录

## 时间

2026-05-24

## Git 分支

`eabi兼容` (基于 `claude` 分支)

## 背景

CCS 20 默认使用 EABI (ELF) 格式替代旧的 COFF 格式。ofd6x.exe (TMS320C6x Object File Display v8.0.1, 2015) 无法解析新的 EABI .out 文件。

## 改动摘要

### 新增文件
- `ofd2000.exe` — 从 CCS 20 安装目录 (ti-cgt-c2000_25.11.0.LTS/bin/) 复制的新版 Object File Display 工具

### 修改文件
- `AddressTool.py` — 4 类改动，COFF 路径零影响

### 改动详情

#### 1. 新增辅助函数
- `_is_eabi_format(dwarf_info)` — 检测 XML 中是否有 `<elf32_ehdr>` 元素，自动判断是 EABI 还是 COFF
- `_find_dwarf_value(die, attr_name)` — 兼容 `<block>` (ofd6x/COFF) 和 `<exprloc>` (ofd2000/EABI) 两种 DWARF 地址标签

#### 2. get_global_variable_address 双路径
- EABI: 遍历 `<elf32_sym>` → `<st_name_string>` / `<st_value>`，变量名无 `_` 前缀，过滤 STB_GLOBAL
- COFF: 遍历 `<symbol>` → `<name>` / `<value>`，变量名有 `_` 前缀（完全原逻辑）
- DIE 回退: 同时尝试 `<exprloc>` 和 `<block>`

#### 3. DWARF 属性查找 (6 处)
所有 `DW_AT_location` / `DW_AT_data_member_location` 的 `<block>` 查找改为 `_find_dwarf_value()` 兼容调用

#### 4. 工具路径和 GUI
- `auto_find_tools()` / `set_default_ofd6x_path()`: 优先 `ofd2000.exe`，回退 `ofd6x.exe`
- `convert_out_to_xml()`: 路径加引号，修复空格路径问题
- GUI 标签: 通用化为 "ofd工具路径"

### 自适应流程

```
用户输入 .out 文件
       ↓
convert_out_to_xml() → ofd2000.exe --xml --dwarf → 生成 XML
       ↓
parse_dwarf_xml() → 解析 XML
       ↓
_is_eabi_format() → 有 <elf32_ehdr>？
   ├── 是 → EABI 路径 (elf32_sym/st_name_string/st_value + exprloc)
   └── 否 → COFF 路径 (symbol/name/value + block) + _ 前缀
```

## 已知问题

1. EABI 编译器 (v25.11) 在 -O0 也会将"只在单个函数内使用的文件作用域变量"降级到栈帧（`DW_OP_bregXX`），这些变量没有固定内存地址。解决：加 `volatile` 关键字。
2. 工具尚未过滤 `DW_OP_bregXX` 类型的非绝对地址，会返回无意义的栈偏移值。

## TODO / 待续

- [x] 过滤非 `DW_OP_addr` 类型的地址，给出有意义的提示 — `_find_dwarf_value()` 自动过滤 `DW_OP_bregXX` / `DW_OP_fbreg`
- [x] 支持拖拽 .out 文件到窗口 — 禁用子控件拖放 + 主窗口 dragEnterEvent/dragMoveEvent/dropEvent
- [ ] 编译一个 COFF 格式的老 .out 文件做完整回归测试
- [ ] 考虑支持 `_linkInfo.xml` 作为 ofd 工具不可用时的 fallback

## 参考路径

- CCS 20 安装: `D:\00_CCS\00_CCS_20`
- 编译器: `ti-cgt-c2000_25.11.0.LTS`
- 示例项目: `C:\Users\Lancer\workspace_ccstheia\Driverlib Empty CPU1 Example CCS Project`
- 老工具源码: `E:\02GitHub\addressTool\AddressTool.py`
