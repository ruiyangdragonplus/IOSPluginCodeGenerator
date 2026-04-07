# iOS 插件代码生成器

一个基于 Python 的 iOS 原生代码批量生成工具，采用词库驱动命名方式，支持 Objective-C、C++ 和 String 常量三种生成模式，具备增量生成、行数控制和自动统计等功能。

## 目录

- [项目简介](#项目简介)
- [生成模式](#生成模式)
- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [配置文件说明](#配置文件说明)
- [命令行参数](#命令行参数)
- [词库说明](#词库说明)
- [输出统计](#输出统计)
- [项目结构](#项目结构)
- [使用示例](#使用示例)
- [性能优化](#性能优化)
- [工具](#工具)
- [统一入口注册表](#统一入口注册表)
- [Unity 集成说明](#unity-集成说明)

---

## 项目简介

### 项目名称
**iOS Plugin Code Generator** - iOS 插件代码生成器

### 主要功能
批量生成 iOS 原生代码文件，用于合规测试场景下的原生代码样板生成，支持：

- **多语言支持**：Objective-C (`.h/.m`)、C++ (`.hpp/.cpp`) 和 String 常量 (`.m/.cpp`)
- **词库驱动命名**：自动组合生成类名、方法名、属性名和 String 内容
- **行数控制**：精确控制总输出行数和单类行数
- **增量生成**：支持多次执行，避免命名重复
- **自动统计**：生成后自动显示代码行数统计报告
- **String 常量模式**：生成包含多个 String 常量的单个文件，支持词汇和句子两种模式

### 技术特点

- 采用 Python 3 实现，跨平台运行
- 配置驱动，所有参数通过 JSON 配置
- 状态持久化，支持断点续生成
- 模块化设计，易于扩展新语言支持
- 适用于 Unity iOS Plugin 测试接入场景

---

## 生成模式

本项目支持 **4 种生成模式**，满足不同的代码生成需求：

| 模式 | 语言 | 输出内容 | 文件扩展名 | 配置方式 |
|------|------|----------|-----------|----------|
| **OC 代码生成** | Objective-C | 类/方法/属性 | `.h` / `.m` | `"language": "objc"` |
| **OC String 生成** | Objective-C | String 常量 | `.m` | `"language": "string", "stringLanguage": "objc"` |
| **C++ 代码生成** | C++ | 类/方法/成员变量 | `.hpp` / `.cpp` | `"language": "cpp"` |
| **C++ String 生成** | C++ | `const char[]` 常量 | `.cpp` | `"language": "string", "stringLanguage": "cpp"` |

### 模式特点

#### 1. OC 代码生成
- 生成完整的 Objective-C 类，包含属性、方法
- 支持 15 种方法模板，8 类代码块
- 支持生成 `ABPluginRegistry.m` 统一调用所有类

#### 2. OC String 生成
- 生成单个文件包含多个 String 常量
- 支持 `word`（词汇组合）和 `sentence`（句子）两种模式
- 自动生成 `ABPrintStringConstants()` 函数

#### 3. C++ 代码生成
- 生成完整的 C++ 类，使用纯 C++ 语法
- 支持 21 种 C++ 方法模板，11 类 C++ 代码块
- 支持生成 `ABPluginRegistry.cpp` 统一调用所有类

#### 4. C++ String 生成
- 生成单个文件包含多个 `const char[]` 常量
- 支持 `word`（词汇组合）和 `sentence`（句子）两种模式
- 自动生成 `ABPrintStringConstants()` 函数

> 📖 **详细文档**: 查看 [docs/MODES.md](docs/MODES.md) 获取完整的模式说明、配置示例和使用示例。

---

## 快速开始

### 环境要求

- **操作系统**：Windows / macOS / Linux
- **Python 版本**：Python 3.6+
- **依赖**：无第三方依赖（仅使用标准库）

### 安装步骤

1. 克隆或下载项目到本地
2. 确保 Python 3 已安装并添加到 PATH
3. 验证 Python 版本：
   ```bash
   python --version
   ```

### 快速使用示例

#### 方式一：使用批处理脚本（Windows）

```bash
run.bat
```

#### 方式二：直接运行 Python 脚本

```bash
python main.py --config ./config/generator.json
```

#### 方式三：使用命令行参数覆盖配置

```bash
python main.py --config ./config/generator.json --language cpp --output ./output/cpp_test
```

---

## 功能特性

### 1. 多语言支持（4 种模式）

本项目支持 4 种生成模式，详细配置请参考 [docs/MODES.md](docs/MODES.md)：

| 模式 | 配置值 | 文件扩展名 |
|------|--------|-----------|
| OC 代码生成 | `"language": "objc"` | `.h` / `.m` |
| OC String 生成 | `"language": "string", "stringLanguage": "objc"` | `.m` |
| C++ 代码生成 | `"language": "cpp"` | `.hpp` / `.cpp` |
| C++ String 生成 | `"language": "string", "stringLanguage": "cpp"` | `.cpp` |

### 2. String 常量生成模式（OC/C++）

**功能说明**：
生成包含随机 String 常量的单个文件，支持 Objective-C (`NSString * const`) 和 C++ (`const char[]`) 格式，适用于 Unity Plugins 中的字符串资源管理。

**详细文档**: 查看 [docs/MODES.md#模式 2-oc-string-生成](docs/MODES.md#模式 2-oc-string-生成) 和 [docs/MODES.md#模式 4-c-string-生成](docs/MODES.md#模式 4-c-string-生成) 获取完整说明。

**配置项**：
```json
{
  "language": "string",
  "outputDir": "./output_string",
  "stringCount": 1000,
  "stringMode": "word",
  "stringLanguage": "objc",
  "randomSeed": 12345
}
```

**配置项说明**：
| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `stringCount` | int | 生成的 String 数量 | 1000 |
| `stringMode` | string | `word`（词汇组合）或 `sentence`（句子模式） | word |
| `stringLanguage` | string | 输出格式：`objc` 或 `cpp` | objc |

**使用示例**：
```bash
# OC String 生成（词汇模式）
python main.py --config ./config/generator_string.json

# C++ String 生成（词汇模式）
python main.py --config ./config/generator_string_cpp.json

# 句子模式
python main.py --config ./config/generator_string_sentence.json
```

### 3. 词库驱动命名

**Objective-C 示例输出：**
```objc
// ABDataCacheManager.h
#import <Foundation/Foundation.h>

@interface ABDataCacheManager : NSObject

@property (nonatomic, assign) NSInteger cachedCount;
@property (nonatomic, strong) NSString *activeState;

- (void)loadCacheIfNeeded;
- (NSInteger)buildSignalForIndex:(NSInteger)index;

@end
```

**C++ 示例输出：**
```cpp
// ABDataCacheManager.hpp
#pragma once

#include <string>
#include <vector>

class ABDataCacheManager {
public:
    ABDataCacheManager();
    ~ABDataCacheManager();
    
    void loadCacheIfNeeded();
    int buildSignalForIndex(int index);

private:
    int cachedCount;
    std::string activeState;
};
```

### 4. 词库驱动命名

所有命名均从词库中组合生成，确保：

- 类名：PascalCase，格式为 `[前缀]+[修饰词]+[中间词]+[名词后缀]`
- 方法名：camelCase，格式为 `[动词]+[对象]+[后缀]`
- 属性名：camelCase，格式为 `[形容词]+[名词]`

### 5. 行数控制

支持多层级行数控制：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `totalLineRange` | 总输出行数范围 | `[400, 1200]` |
| `linesPerClassRange` | 单类行数范围 | `[60, 180]` |
| `methodsPerClassRange` | 每类方法数量范围 | `[4, 15]` |
| `propertiesPerClassRange` | 每类属性数量范围 | `[2, 5]` |

### 6. 增量生成

- 通过状态文件记录已使用的命名
- 后续生成自动跳过已使用的类名、方法名
- 支持多次执行累积生成大量文件
- 状态文件损坏时自动备份并重建

### 7. 自动统计报告

生成完成后自动显示：

- 总文件数及按扩展名分类统计
- 总行数、代码行数、空行数、注释行数
- Top 10 最大文件列表
- 按扩展名汇总的详细统计

---

## 配置文件说明

### `generator.json` 配置项详解

```json
{
  "language": "objc",
  "outputDir": "./output",
  "classCount": 6,
  "totalLineRange": [400, 1200],
  "linesPerClassRange": [60, 180],
  "methodsPerClassRange": [4, 15],
  "propertiesPerClassRange": [2, 5],
  "classPrefix": "AB",
  "incremental": true,
  "overwrite": false,
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true,
  "generateRegistry": true,
  "registryLanguage": "objc"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `language` | string | 是 | - | 生成模式：`objc`（OC 代码）、`cpp`（C++ 代码）、`string`（String 常量） |
| `outputDir` | string | 是 | - | 输出目录路径 |
| `classCount` | int | 条件 | - | 生成类的数量（非 string 模式必填） |
| `stringCount` | int | 条件 | `1000` | String 数量（string 模式） |
| `stringMode` | string | 否 | `word` | String 模式：`word` 或 `sentence` |
| `stringLanguage` | string | 否 | `objc` | String 输出语言：`objc` 或 `cpp` |
| `totalLineRange` | int[] | 是 | - | 总输出行数范围 [min, max] |
| `linesPerClassRange` | int[] | 是 | - | 单类行数范围 [min, max] |
| `methodsPerClassRange` | int[] | 是 | - | 每类方法数量范围 [min, max] |
| `propertiesPerClassRange` | int[] | 是 | - | 每类属性数量范围 [min, max] |
| `classPrefix` | string | 否 | `""` | 类名前缀（如 `AB`） |
| `incremental` | bool | 否 | `true` | 是否增量生成 |
| `overwrite` | bool | 否 | `false` | 是否覆盖已存在文件 |
| `randomSeed` | int | 否 | `12345` | 随机种子，用于复现结果 |
| `stateFile` | string | 是 | - | 状态文件路径 |
| `vocabularyFile` | string | 是 | - | 词库文件路径 |
| `showStats` | bool | 否 | `true` | 是否显示统计报告 |
| `generateRegistry` | bool | 否 | `false` | 是否生成统一入口注册表文件 |
| `registryLanguage` | string | 否 | `objc` | 注册表语言：`objc` 或 `cpp` |

**String 模式配置示例：**
```json
{
  "language": "string",
  "outputDir": "./output_string",
  "stringCount": 1000,
  "stringMode": "word",
  "stringLanguage": "objc",
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true
}
```

### `vocabulary.json` 词库结构

```json
{
  "class": {
    "prefix": ["Data", "Core", "Rapid", "Safe", ...],
    "middle": ["Cache", "Signal", "Pixel", "Vector", ...],
    "suffixNoun": ["Manager", "Handler", "Store", "Service", ...]
  },
  "method": {
    "verb": ["load", "fetch", "build", "update", ...],
    "object": ["Cache", "Signal", "Config", "Buffer", ...],
    "suffix": ["IfNeeded", "WithOptions", "Safely", ...]
  },
  "property": {
    "adjective": ["current", "active", "cached", "local", ...],
    "noun": ["Value", "Config", "Index", "Buffer", ...]
  }
}
```

### `state.json` 状态文件说明

```json
{
  "usedClassNames": ["ABAboveAlertSector", "ABAboveBarrierMicrophone", ...],
  "usedMethodNames": ["loadCacheIfNeeded", "buildSignalWithOptions", ...],
  "usedWordCombos": [],
  "generatedFiles": ["/path/to/file1.h", "/path/to/file1.m", ...],
  "history": [
    {
      "language": "objc",
      "generated_classes": ["ABClass1", "ABClass2"],
      "total_lines": 842,
      "files_written": 12,
      "files_skipped": 0
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `usedClassNames` | string[] | 已使用的类名列表 |
| `usedMethodNames` | string[] | 已使用的方法名列表 |
| `usedWordCombos` | string[] | 已使用的词汇组合 |
| `generatedFiles` | string[] | 已生成的文件路径列表 |
| `history` | object[] | 执行历史记录 |

---

## 命令行参数

### 所有可用参数及说明

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--config` | - | 配置文件路径 | `--config ./config/generator.json` |
| `--language` | - | 覆盖配置中的语言选项 | `--language string` |
| `--seed` | - | 覆盖随机种子 | `--seed 999` |
| `--output` | - | 覆盖输出目录 | `--output D:/Generated/` |
| `--help` | `-h` | 显示帮助信息 | `--help` |

### 使用示例

#### 基本使用
```bash
python main.py --config ./config/generator.json
```

#### 指定语言
```bash
python main.py --config ./config/generator.json --language cpp
```

#### String 模式生成
```bash
python main.py --config ./config/generator_string.json
```

#### 指定随机种子（用于复现）
```bash
python main.py --config ./config/generator.json --seed 42
```

#### 指定输出目录
```bash
python main.py --config ./config/generator.json --output ./output/custom
```

#### 组合使用
```bash
python main.py --config ./config/generator.json --language cpp --seed 42 --output ./output/cpp_test
```

---

## 词库说明

### 词库结构

词库分为三大类，每类包含多个子类别：

#### 1. 类名词库 (`class`)
- **prefix**：前缀修饰词（如 `Data`, `Core`, `Rapid`）
- **middle**：中间词（如 `Cache`, `Signal`, `Vector`）
- **suffixNoun**：名词后缀（如 `Manager`, `Handler`, `Service`）

#### 2. 方法词库 (`method`)
- **verb**：动词（如 `load`, `fetch`, `build`）
- **object**：对象名词（如 `Cache`, `Signal`, `Config`）
- **suffix**：方法后缀（如 `IfNeeded`, `WithOptions`）

#### 3. 属性词库 (`property`)
- **adjective**：形容词（如 `current`, `active`, `cached`）
- **noun**：名词（如 `Value`, `Config`, `Index`）

### 当前词库规模

当前默认词库 [`config/vocabulary.json`](config/vocabulary.json) 包含：

| 类别 | 子类别 | 词汇数量 |
|------|--------|----------|
| 类名 | prefix | 350+ |
| 类名 | middle | 250+ |
| 类名 | suffixNoun | 250+ |
| 方法 | verb | 200+ |
| 方法 | object | 200+ |
| 方法 | suffix | 100+ |
| 属性 | adjective | 200+ |
| 属性 | noun | 200+ |
| **总计** | - | **约 2370 个词汇** |

### 命名组合潜力

基于当前词库规模，理论命名组合数量：

- **类名组合**：350 × 250 × 250 ≈ **21,875,000 种**
- **方法名组合**：200 × 200 × 100 = **4,000,000 种**
- **属性名组合**：200 × 200 = **40,000 种**

**总计超过 3500 万种可能的命名组合**，足以支持大规模代码生成需求。

---

## 输出统计

### 自动显示行数统计

生成完成后，工具会自动调用 [`tools/line_counter.py`](tools/line_counter.py) 显示统计报告。

### 统计内容说明

统计报告包含以下内容：

1. **文件统计**
   - 总文件数
   - 按扩展名分类统计（`.h`, `.m`, `.hpp`, `.cpp`）

2. **行数统计**
   - 总行数
   - 代码行数（非空非注释）
   - 空行数
   - 注释行数

3. **Top 10 最大文件**
   - 按行数排序的前 10 个文件

4. **按扩展名汇总**
   - 每种文件类型的详细统计

### 统计报告示例

```
========================================
代码行数统计报告
========================================
目标目录：./output

文件统计:
  总文件数：12
  .h 文件：6
  .m 文件：6

行数统计:
  总行数：842
  代码行数：650
  空行数：120
  注释行数：72

Top 10 最大文件:
  1. ABDataCacheManager.m - 95 行
  2. ABSignalHandler.m - 88 行
  3. ABVectorBuilder.m - 82 行
  ...

按扩展名汇总:
  .h:
    文件数：6
    总行数：320
    代码行数：280
    空行数：25
    注释行数：15
  .m:
    文件数：6
    总行数：522
    代码行数：370
    空行数：95
    注释行数：57

========================================
```

---

## 项目结构

### 目录结构

```
IOSPluginCodeGenerator/
├── main.py                 # 主入口文件
├── run.bat                 # Windows 批处理启动脚本
├── ReadMe.md               # 项目文档
├── config/                 # 配置文件目录
│   ├── generator.json      # 主配置文件
│   ├── vocabulary.json     # 词库配置文件
│   └── state.json          # 状态文件（自动生成）
├── core/                   # 核心模块目录
│   ├── __init__.py
│   ├── config_loader.py    # 配置加载器
│   ├── state_store.py      # 状态存储器
│   ├── name_builder.py     # 命名构建器
│   ├── line_budget.py      # 行数预算分配器
│   ├── file_writer.py      # 文件写入器
│   ├── objc_generator.py   # Objective-C 生成器
│   ├── cpp_generator.py    # C++ 生成器
│   └── string_generator.py # String 常量生成器
└── tools/                  # 工具脚本目录
    └── line_counter.py     # 代码行数统计工具
```

### 核心模块说明

| 模块 | 文件 | 职责 |
|------|------|------|
| 主入口 | [`main.py`](main.py) | 流程编排：加载配置 → 初始化状态 → 生成命名 → 生成代码 → 写入文件 |
| 配置加载器 | [`core/config_loader.py`](core/config_loader.py) | 读取 JSON 配置、校验字段、提供默认值 |
| 状态存储器 | [`core/state_store.py`](core/state_store.py) | 加载/保存状态文件，记录已使用命名和已生成文件 |
| 命名构建器 | [`core/name_builder.py`](core/name_builder.py) | 根据词库生成类名、方法名、属性名，确保唯一性 |
| 行数预算 | [`core/line_budget.py`](core/line_budget.py) | 分配行数预算，控制方法复杂度 |
| 文件写入器 | [`core/file_writer.py`](core/file_writer.py) | 输出文件到磁盘，处理目录创建和覆盖策略 |
| ObjC 生成器 | [`core/objc_generator.py`](core/objc_generator.py) | 生成 Objective-C 头文件和实现文件 |
| C++ 生成器 | [`core/cpp_generator.py`](core/cpp_generator.py) | 生成 C++ 头文件和实现文件 |
| String 生成器 | [`core/string_generator.py`](core/string_generator.py) | 生成 String 常量文件，支持 Objective-C 和 C++ 格式，提供词汇组合和句子两种模式 |
| 行数统计 | [`tools/line_counter.py`](tools/line_counter.py) | 统计代码行数，生成统计报告 |

---

## 使用示例

> 📖 **完整模式文档**: 查看 [docs/MODES.md](docs/MODES.md) 获取 4 种生成模式的详细说明、配置示例和完整使用流程。

### 快速参考

| 模式 | 配置文件示例 | 命令 |
|------|-------------|------|
| OC 代码生成 | `generator.json` | `python main.py --config ./config/generator.json` |
| OC String 生成 | `generator_string.json` | `python main.py --config ./config/generator_string.json` |
| C++ 代码生成 | `generator.json` | `python main.py --config ./config/generator.json --language cpp` |
| C++ String 生成 | `generator_string_cpp.json` | `python main.py --config ./config/generator_string_cpp.json` |

### 基本使用

生成 6 个 Objective-C 类：

```bash
python main.py --config ./config/generator.json
```

### C++ 生成示例

生成 C++ 代码：

```bash
python main.py --config ./config/generator.json --language cpp
```

或使用预配置的 C++ 配置文件：

```bash
python main.py --config ./config/generator_test5.json
```

### String 模式生成示例

生成 1000 个 String 常量（Objective-C 格式）：

```bash
python main.py --config ./config/generator_string.json
```

生成 50 个 String 常量（C++ 格式）：

```bash
python main.py --config ./config/generator_string_cpp.json
```

生成句子模式的 String 常量：

```bash
python main.py --config ./config/generator_string_sentence.json
```

### 大规模生成示例

生成 100 万个类（需要充足磁盘空间）：

```bash
python main.py --config ./config/generator_1m.json
```

**注意**：大规模生成时建议：
1. 确保有足够的磁盘空间
2. 使用 SSD 硬盘以提高写入速度
3. 考虑分批生成，避免单次生成过多文件

### 增量生成示例

第一次生成：

```bash
python main.py --config ./config/generator.json
```

第二次生成（自动跳过已使用的命名）：

```bash
python main.py --config ./config/generator.json
```

两次生成的类名和方法名不会重复。

### 自定义输出目录

```bash
python main.py --config ./config/generator.json --output D:/UnityProject/Assets/Plugins/iOS/Generated
```

### 固定随机种子（用于复现）

```bash
python main.py --config ./config/generator.json --seed 42
```

---

## 性能优化

### 性能优化说明（O(n²)→O(n)）

状态存储模块 [`core/state_store.py`](core/state_store.py) 进行了性能优化：

**优化前**：使用 list 存储已使用命名，每次检查需要 O(n) 时间复杂度

**优化后**：使用 set 进行 O(1) 查找，保存时转换为 list 保持 JSON 兼容性

```python
# 内部使用 set 进行 O(1) 查找
self._usedClassNames: Set[str] = set()
self._usedMethodNames: Set[str] = set()

# 保存时转换为 list 保持 JSON 兼容性
self.state["usedClassNames"] = list(self._usedClassNames)
```

### 大规模生成建议

1. **使用 SSD 硬盘**：文件写入速度更快
2. **分批生成**：避免单次生成过多文件导致内存占用过高
3. **关闭统计报告**：设置 `"showStats": false` 可略微提升性能
4. **增加随机种子**：使用不同的 `randomSeed` 值生成不同批次
5. **监控状态文件大小**：长期增量生成后，状态文件可能变大，可定期归档

---

## 工具

### `tools/line_counter.py` 使用说明

独立的代码行数统计工具，可单独使用。

#### 基本用法

```bash
python tools/line_counter.py ./output
```

#### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `target_dir` | 目标文件夹路径（必填） | - |
| `--extensions` | 要统计的文件扩展名，逗号分隔 | `.h,.m,.hpp,.cpp` |
| `--output` | 输出格式：`text` 或 `json` | `text` |
| `--exclude` | 排除的文件夹模式，逗号分隔 | - |

#### 使用示例

统计指定目录：
```bash
python tools/line_counter.py ./output
```

指定扩展名：
```bash
python tools/line_counter.py ./src --extensions .h,.m,.cpp
```

输出 JSON 格式：
```bash
python tools/line_counter.py ./output --output json
```

排除特定文件夹：
```bash
python tools/line_counter.py ./output --exclude build,dist,node_modules
```

---

## 统一入口注册表

### 功能说明

统一入口注册表功能允许在生成代码后自动生成一个统一的初始化和清理入口文件，方便批量管理所有生成的插件类。

### 配置方式

在 `generator.json` 中添加以下配置：

```json
{
  "generateRegistry": true,      // 是否生成统一入口注册表
  "registryLanguage": "objc"     // 注册表语言：objc 或 cpp
}
```

### 生成的文件

| 文件 | 说明 |
|------|------|
| `ABPluginRegistry.h` | 头文件，声明统一入口函数 |
| `ABPluginRegistry.m` | Objective-C 实现文件（当 `registryLanguage` 为 `objc`） |
| `ABPluginRegistry.cpp` | C++ 实现文件（当 `registryLanguage` 为 `cpp`） |

### Objective-C 注册表示例

```objc
// ABPluginRegistry.m
#import <Foundation/Foundation.h>
#import "ABDataCacheManager.h"
#import "ABDataVectorManager.h"
// ... 导入所有生成的类

// 统一初始化入口
void ABInitializeAllPlugins() {
    if (ABPluginsInitialized) return;
    ABPluginsInitialized = YES;
    
    NSLog(@"[ABPlugin] Initializing all plugins...");
    
    // 自动实例化并调用所有生成的类
    ABDataCacheManager *m1 = [[ABDataCacheManager alloc] init];
    [m1 loadData];
    
    ABDataVectorManager *m2 = [[ABDataVectorManager alloc] init];
    [m2 loadData];
    
    // ... 所有类
    
    NSLog(@"[ABPlugin] All plugins initialized successfully.");
}

// 统一清理入口
void ABCleanupAllPlugins() {
    if (!ABPluginsInitialized) return;
    
    NSLog(@"[ABPlugin] Cleaning up all plugins...");
    
    // 清理逻辑
    ABPluginsInitialized = NO;
    
    NSLog(@"[ABPlugin] All plugins cleaned up successfully.");
}
```

### C++ 注册表示例

```cpp
// ABPluginRegistry.cpp
#include "ABDataCacheManager.h"
#include "ABDataVectorManager.h"
// ...

extern "C" {
    void ABInitializeAllPlugins() {
        if (g_ABPluginsInitialized) return;
        g_ABPluginsInitialized = true;
        
        std::cout << "[ABPlugin] Initializing all plugins..." << std::endl;
        
        // 实例化并调用所有生成的类
        ABDataCacheManager* m1 = new ABDataCacheManager();
        m1->loadData();
        delete m1;
        
        // ... 所有类
        
        std::cout << "[ABPlugin] All plugins initialized successfully." << std::endl;
    }
    
    void ABCleanupAllPlugins() {
        if (!g_ABPluginsInitialized) return;
        
        std::cout << "[ABPlugin] Cleaning up all plugins..." << std::endl;
        
        // 清理逻辑
        g_ABPluginsInitialized = false;
        
        std::cout << "[ABPlugin] All plugins cleaned up successfully." << std::endl;
    }
}
```

### 使用方式

#### 在 Unity 中调用

1. 将生成的 `ABPluginRegistry.h` 和 `ABPluginRegistry.m`（或 `.cpp`）文件复制到 Unity 项目的 `Assets/Plugins/iOS/` 目录

2. 在 C# 代码中使用 `DllImport` 调用：

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

public class ABPluginWrapper
{
    [DllImport("__Internal")]
    private static extern void ABInitializeAllPlugins();
    
    [DllImport("__Internal")]
    private static extern void ABCleanupAllPlugins();
    
    public static void InitializeAll()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABInitializeAllPlugins();
        #endif
    }
    
    public static void CleanupAll()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABCleanupAllPlugins();
        #endif
    }
}
```

3. 在应用启动时调用初始化：

```csharp
void Start()
{
    ABPluginWrapper.InitializeAll();
}

void OnApplicationQuit()
{
    ABPluginWrapper.CleanupAll();
}
```

### C# 包装类模板

项目提供了完整的 C# 包装类模板，位于 [`docs/PluginWrapper.cs`](docs/PluginWrapper.cs)。

---

## 常见问题

### Q: 如何重置生成状态？
A: 删除或清空 `config/state.json` 文件即可重新开始生成。

### Q: 生成的代码可以编译吗？
A: 是的，生成的代码满足基本语法要求，可以直接编译。但仅作为测试样板代码，不包含实际业务逻辑。

### Q: 如何扩展词库？
A: 编辑 `config/vocabulary.json` 文件，在对应类别的数组中添加新词汇即可。

### Q: 支持生成其他语言吗？
A: 当前支持 Objective-C、C++ 和 String 常量模式。如需扩展其他语言，可参考现有生成器模块实现新的生成器类。

---

## Unity 集成说明

生成的代码可以直接用于 Unity iOS 项目。详细的集成说明请参考：

**[Unity iOS 插件集成说明](docs/unity_integration.md)**

### 集成内容概览

| 生成模式 | 说明 | 集成文档章节 |
|----------|------|-------------|
| **普通模式（类/方法/属性）** | 生成完整的 Objective-C 类，包含类定义、属性、实例方法和类方法 | [第 2 章 - 普通代码生成模式](docs/unity_integration.md) |
| **函数模式** | 生成全局函数的 Objective-C 代码 | [第 3 章 - Objective-C 代码调用（函数模式）](docs/unity_integration.md) |
| **C++ 模式** | 生成 C++ 类或函数代码 | [第 4 章 - C++ 代码调用](docs/unity_integration.md) |
| **String 常量模式** | 生成字符串常量定义 | [第 5 章 - 完整示例](docs/unity_integration.md) |

### 快速集成步骤

1. **复制文件**：将生成的 `.h` 和 `.m` 文件复制到 Unity 项目的 `Assets/Plugins/iOS/` 目录
2. **创建 C# 包装类**：
   - **普通模式**：使用工厂函数模式，通过 `ClassName_Create` 创建实例，`ClassName_Destroy` 释放实例
   - **函数模式**：使用 `DllImport("__Internal")` 声明原生方法
3. **平台条件编译**：使用 `#if UNITY_IOS && !UNITY_EDITOR` 避免编辑器中调用
4. **构建设置**：关闭 `Strip Engine Code`，确保原生代码不被剥离

### 普通模式示例（类/方法/属性）

#### 生成的 Objective-C 类
```objc
// ABDataCacheManager.h
@interface ABDataCacheManager : NSObject
@property (nonatomic, strong) NSString *cacheKey;
- (instancetype)initWithCacheKey:(NSString *)key;
- (void)loadData;
- (NSString *)getData;
+ (void)clearAllCache;
@end
```

#### C# 包装类（工厂函数模式）
```csharp
using System;
using System.Runtime.InteropServices;
using UnityEngine;

public class ABDataCacheManagerWrapper : IDisposable
{
    private System.IntPtr nativePtr;
    
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern System.IntPtr ABDataCacheManager_Create(string key);
    
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_Destroy(System.IntPtr ptr);
    
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_LoadData(System.IntPtr ptr);
    
    [DllImport("__Internal")]
    private static extern System.IntPtr ABDataCacheManager_GetData(System.IntPtr ptr);
    
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_ClearAllCache();
    #endif
    
    public ABDataCacheManagerWrapper(string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        nativePtr = ABDataCacheManager_Create(key);
        #endif
    }
    
    public void LoadData()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_LoadData(nativePtr);
        #endif
    }
    
    public string GetData()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        System.IntPtr ptr = ABDataCacheManager_GetData(nativePtr);
        return Marshal.PtrToStringAnsi(ptr);
        #else
        return string.Empty;
        #endif
    }
    
    public static void ClearAllCache()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_ClearAllCache();
        #endif
    }
    
    public void Dispose()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        if (nativePtr != System.IntPtr.Zero)
        {
            ABDataCacheManager_Destroy(nativePtr);
            nativePtr = System.IntPtr.Zero;
        }
        #endif
        GC.SuppressFinalize(this);
    }
}
```

### 函数模式示例

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

public class iOSPluginWrapper
{
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern void ABPrintStringConstants();
    #endif
    
    public static void PrintConstants()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABPrintStringConstants();
        #else
        Debug.Log("[iOS Plugin] Running in Editor");
        #endif
    }
}
```

---

## 许可证

本项目仅供学习和测试使用。
