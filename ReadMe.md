# iOS 原生代码生成工具技术方案文档

## 1. 项目概述

### 1.1 项目目标
开发一个运行于 Windows 环境的代码生成工具，用于**合规测试场景**下批量生成 iOS 原生代码文件，支持：

- 按配置选择生成 **Objective-C** 或 **C++**
- 输出到指定目录
- 允许配置词库，自动组合生成：
  - 类名
  - 方法名
- 支持配置：
  - 生成类个数
  - 总输出行数范围
  - 每类方法数量范围
  - 每类属性数量范围
- 支持增量生成
- 使用状态文件记录已使用命名，避免重复
- 生成结果可放入 Unity 工程的 `Assets/Plugins/iOS/` 或其子目录中，供 Unity iOS Plugin 集成

---

## 2. 适用范围

### 2.1 适用场景
本工具用于以下合规用途：

- 测试工程中的原生代码样板生成
- Unity iOS Plugin 测试接入
- 原生层接口演示代码生成
- 批量生成可编译的示例类

### 2.2 非目标范围
本工具不涉及：

- 绕过平台审核
- 规避合规检测
- 生成伪装业务逻辑的代码

---

## 3. 总体技术选型

## 3.1 选型结论
采用 **Python 3** 作为主实现语言。

## 3.2 选型原因

### Python 的优势
- 适合文本模板生成
- JSON 支持原生且稳定
- 文件与目录操作方便
- 开发速度快
- 易于维护命名状态
- 易于扩展更多输出语言
- 可在 Windows 环境运行
- 可被 Unity Editor 通过外部进程调用

## 3.3 备选方案说明
可选方案包括 Node.js、C#、Shell、Batch，但综合考虑开发效率、可维护性、模板能力、增量状态管理能力后，Python 最优。

---

## 4. 功能需求

## 4.1 基础功能

### 4.1.1 输出语言选择
支持两种输出语言：

- `objc`
- `cpp`

执行时仅选择其中一种进行生成。

### 4.1.2 输出目录控制
支持通过 JSON 配置指定输出目录。

要求：
- 若目录不存在，可自动创建
- 若目录存在，支持增量追加生成
- 默认不覆盖同名文件

### 4.1.3 词库驱动命名
允许通过配置文件定义常用词汇，并按规则自动组合生成：

- 类名
- 方法名
- 属性名
- 局部变量名（可选）

### 4.1.4 类生成数量控制
允许指定生成类个数。

### 4.1.5 总行数范围控制
允许配置输出文件总行数范围，例如：

```json
"totalLineRange": [800, 1200]
```

生成器需尽量保证总输出行数落在该范围内。

### 4.1.6 增量生成
支持多次执行，后续生成需避免重复使用已有类名、方法名、词汇组合。

### 4.1.7 状态持久化
通过状态文件记录：

- 已使用类名
- 已使用方法名
- 已使用词汇组合
- 已生成文件
- 上次执行信息

---

## 4.2 命名规则

### 4.2.1 类名规则
- 使用 PascalCase
- 可以带统一前缀
- 结尾必须为名词
- 不允许重复

示例：
- `ABDataCacheManager`
- `ABPixelSignalStore`

### 4.2.2 方法名规则
- 使用 camelCase
- 必须以动词开头
- 不允许重复

示例：
- `loadCacheIfNeeded`
- `updateSignalWithOptions`

### 4.2.3 属性名规则
- 使用 camelCase
- 推荐使用名词或形容词+名词
- 不要求全局唯一，但类内不能重复

---

## 4.3 输出文件规则

### 4.3.1 Objective-C 模式
每个类输出：

- `ClassName.h`
- `ClassName.m`

### 4.3.2 C++ 模式
每个类输出：

- `ClassName.hpp`
- `ClassName.cpp`

### 4.3.3 文件内容要求
生成文件需满足：

- 基本语法正确
- 可编译
- 引用关系完整
- 包含合理的方法声明与实现
- 行数可控

---

## 4.4 Unity 接入要求

### 4.4.1 目录兼容性
输出目录需支持 Unity iOS 原生插件目录结构，例如：

```txt
Assets/Plugins/iOS/Generated/
```

### 4.4.2 文件兼容性
生成文件扩展名符合 Unity 导出 Xcode 工程时的识别方式：

- `.h`
- `.m`
- `.hpp`
- `.cpp`

### 4.4.3 后续可扩展方向
后续可增加：
- `.mm` Objective-C++ 桥接层
- `extern "C"` 导出函数包装
- Unity C# 调用桥接代码生成

---

## 5. 非功能需求

## 5.1 运行环境
- 操作系统：Windows
- 运行方式：
  - Python 命令行
  - 可选 batch 启动
  - 可选 Unity Editor 间接调用

## 5.2 可维护性
- 模块化结构清晰
- 模板与逻辑分离
- 配置与状态分离

## 5.3 可扩展性
未来应易于扩展：
- 更多目标语言
- 更多代码模板
- 更复杂的方法体
- Unity Editor GUI

## 5.4 稳定性
- 错误配置有清晰提示
- 名称冲突时有回退策略
- 状态文件损坏时有恢复机制

---

## 6. 系统架构设计

## 6.1 总体架构

```txt
+-------------------+
|   CLI / Batch     |
+---------+---------+
          |
          v
+-------------------+
|     main.py       |
+---------+---------+
          |
          v
+-------------------+
|  Config Loader    |
+---------+---------+
          |
          v
+-------------------+
|   State Store     |
+---------+---------+
          |
          v
+-------------------+
|   Name Builder    |
+---------+---------+
          |
          v
+-------------------+
| Language Generator|
|  - ObjC Generator |
|  - Cpp Generator  |
+---------+---------+
          |
          v
+-------------------+
|   File Writer     |
+-------------------+
```

---

## 6.2 模块划分

### 6.2.1 `main.py`
职责：
- 读取命令行参数
- 加载配置
- 初始化状态
- 调用目标语言生成器
- 汇总输出结果

### 6.2.2 `config_loader.py`
职责：
- 读取 JSON 配置
- 校验字段完整性
- 提供默认值
- 将配置转换为内部对象

### 6.2.3 `state_store.py`
职责：
- 加载状态文件
- 维护已使用类名/方法名/组合
- 保存状态

### 6.2.4 `name_builder.py`
职责：
- 根据词库生成类名
- 根据词库生成方法名
- 确保规则正确
- 确保全局不重复

### 6.2.5 `objc_generator.py`
职责：
- 生成 Objective-C 头文件和实现文件
- 控制方法、属性、注释、行数分布

### 6.2.6 `cpp_generator.py`
职责：
- 生成 C++ 头文件和实现文件
- 控制方法、属性、命名空间、行数分布

### 6.2.7 `line_budget.py`
职责：
- 根据总行数范围分配各类行数预算
- 控制每个文件的输出规模

### 6.2.8 `file_writer.py`
职责：
- 输出文件
- 创建目录
- 检查覆盖策略
- 输出写入报告

---

## 7. 项目目录结构

```txt
codegen_tool/
├─ main.py
├─ run.bat
├─ config/
│  ├─ generator.json
│  ├─ vocabulary.json
│  └─ state.json
├─ core/
│  ├─ config_loader.py
│  ├─ state_store.py
│  ├─ name_builder.py
│  ├─ line_budget.py
│  ├─ file_writer.py
│  ├─ objc_generator.py
│  └─ cpp_generator.py
├─ models/
│  ├─ config_models.py
│  └─ code_models.py
├─ templates/
│  ├─ objc_header.tpl
│  ├─ objc_impl.tpl
│  ├─ cpp_header.tpl
│  └─ cpp_impl.tpl
└─ output/
```

---

## 8. 配置设计

## 8.1 主配置 `generator.json`

```json
{
  "language": "objc",
  "outputDir": "D:/UnityProject/Assets/Plugins/iOS/Generated",
  "classCount": 6,
  "totalLineRange": [500, 900],
  "linesPerClassRange": [60, 180],
  "methodsPerClassRange": [4, 8],
  "propertiesPerClassRange": [2, 5],
  "classPrefix": "AB",
  "incremental": true,
  "overwrite": false,
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| language | string | 是 | `objc` 或 `cpp` |
| outputDir | string | 是 | 输出目录 |
| classCount | int | 是 | 生成类个数 |
| totalLineRange | int[2] | 是 | 总输出行数范围 |
| linesPerClassRange | int[2] | 是 | 单类行数范围 |
| methodsPerClassRange | int[2] | 是 | 每类方法数量范围 |
| propertiesPerClassRange | int[2] | 是 | 每类属性数量范围 |
| classPrefix | string | 否 | 类名前缀 |
| incremental | bool | 否 | 是否增量生成 |
| overwrite | bool | 否 | 是否允许覆盖文件 |
| randomSeed | int | 否 | 随机种子，便于复现 |
| stateFile | string | 是 | 状态文件路径 |
| vocabularyFile | string | 是 | 词库文件路径 |

---

## 8.2 词库配置 `vocabulary.json`

```json
{
  "class": {
    "prefix": ["Data", "Core", "Rapid", "Safe", "Smart"],
    "middle": ["Cache", "Signal", "Pixel", "Vector", "Buffer"],
    "suffixNoun": ["Manager", "Handler", "Store", "Service", "Builder"]
  },
  "method": {
    "verb": ["load", "fetch", "build", "update", "merge", "reset"],
    "object": ["Cache", "Signal", "Config", "Buffer", "Record", "Value"],
    "suffix": ["IfNeeded", "WithOptions", "Safely", "ForIndex", "InRange"]
  },
  "property": {
    "adjective": ["current", "active", "cached", "local", "shared"],
    "noun": ["Value", "Config", "Index", "Buffer", "State", "Count"]
  }
}
```

---

## 8.3 状态文件 `state.json`

```json
{
  "usedClassNames": [],
  "usedMethodNames": [],
  "usedWordCombos": [],
  "generatedFiles": [],
  "history": []
}
```

### 字段说明
- `usedClassNames`：已使用类名
- `usedMethodNames`：已使用方法名
- `usedWordCombos`：已使用词汇组合
- `generatedFiles`：已输出文件
- `history`：执行历史

---

## 9. 生成规则设计

## 9.1 类名生成规则
类名组成：

```txt
[classPrefix] + class.prefix + class.middle + class.suffixNoun
```

示例：

```txt
AB + Rapid + Buffer + Manager
= ABRapidBufferManager
```

### 约束
- PascalCase
- suffix 必须来自 `suffixNoun`
- 全局唯一
- 若冲突则重试组合

---

## 9.2 方法名生成规则
方法名组成：

```txt
method.verb + method.object + method.suffix
```

示例：

```txt
build + Cache + IfNeeded
= buildCacheIfNeeded
```

### 约束
- camelCase
- 必须动词开头
- 全局唯一
- 若冲突则重试组合

---

## 9.3 属性名生成规则
属性名组成：

```txt
property.adjective + property.noun
```

示例：

```txt
cached + Buffer
= cachedBuffer
```

### 约束
- camelCase
- 类内唯一

---

## 10. 行数控制设计

## 10.1 控制目标
需要使本次生成的输出总行数落在配置区间内。

## 10.2 控制策略
采用两层控制：

### 第一层：类级预算
依据：
- `classCount`
- `linesPerClassRange`
- `totalLineRange`

先为每个类分配一个目标行数。

### 第二层：文件级填充
每个类生成时，根据预算自动调节：
- 属性数量
- 方法数量
- 方法体复杂度
- 注释数量
- 空行数量（可少量使用）

---

## 10.3 方法体复杂度分级

### Level 1：简单方法
- 1~3 行逻辑
- 适合 getter / reset / assign

### Level 2：中等方法
- 4~8 行逻辑
- 包含条件判断、局部变量

### Level 3：复杂方法
- 8~15 行逻辑
- 包含循环、分支、聚合计算

生成器可随机组合不同复杂度方法，以控制总行数。

---

## 11. Objective-C 代码生成设计

## 11.1 文件结构

### 头文件 `.h`
内容包括：
- `#import <Foundation/Foundation.h>`
- 接口声明
- 属性声明
- 方法声明

### 实现文件 `.m`
内容包括：
- `#import "ClassName.h"`
- `@implementation`
- 属性初始化
- 方法实现

---

## 11.2 示例结构

```objc
#import <Foundation/Foundation.h>

@interface ABDataCacheManager : NSObject

@property (nonatomic, assign) NSInteger cachedCount;
@property (nonatomic, strong) NSString *activeState;

- (void)loadCacheIfNeeded;
- (NSInteger)buildSignalForIndex:(NSInteger)index;

@end
```

---

## 12. C++ 代码生成设计

## 12.1 文件结构

### 头文件 `.hpp`
内容包括：
- `#pragma once`
- `#include <string>`
- `#include <vector>`
- 类声明
- 成员变量
- 成员函数声明

### 实现文件 `.cpp`
内容包括：
- `#include "ClassName.hpp"`
- 方法实现

---

## 12.2 示例结构

```cpp
#pragma once

#include <string>
#include <vector>

class ABDataCacheManager {
public:
    ABDataCacheManager();
    void loadCacheIfNeeded();
    int buildSignalForIndex(int index);

private:
    int cachedCount;
    std::string activeState;
};
```

---

## 13. 增量生成设计

## 13.1 核心目标
避免以下内容重复：
- 类名
- 方法名
- 词汇组合
- 文件名

## 13.2 实现机制
每次生成前：
1. 读取 `state.json`
2. 导入所有历史使用记录
3. 生成新命名时检查冲突
4. 输出成功后更新状态文件

## 13.3 冲突处理
若重试达到阈值仍冲突，则：
- 增加随机数字后缀，或
- 切换备用词汇组合

建议默认先重试组合，避免使用数字后缀。

---

## 14. 错误处理设计

## 14.1 配置错误
场景：
- JSON 格式错误
- 缺少必填字段
- range 配置非法

处理：
- 直接报错并退出
- 输出明确错误位置

## 14.2 词库不足
场景：
- 可用组合数量不足
- 无法满足唯一命名

处理：
- 提示扩充词库
- 输出当前可用组合上限

## 14.3 文件冲突
场景：
- 输出文件已存在
- overwrite=false

处理：
- 跳过或报错
- 在日志中记录

## 14.4 状态文件损坏
处理：
- 自动备份损坏文件
- 重建空状态
- 输出警告信息

---

## 15. 日志与输出设计

## 15.1 控制台日志
输出内容包括：
- 当前语言模式
- 输出目录
- 配置摘要
- 生成类名
- 文件写入结果
- 总行数统计
- 状态更新结果

## 15.2 执行结果摘要
建议输出：

```txt
Language: objc
OutputDir: D:/UnityProject/Assets/Plugins/iOS/Generated
GeneratedClasses: 6
GeneratedFiles: 12
TotalLines: 842
StateUpdated: true
```

---

## 16. 命令行设计

## 16.1 基本命令
```bash
python main.py --config ./config/generator.json
```

## 16.2 可选参数
```bash
python main.py --config ./config/generator.json --language objc
python main.py --config ./config/generator.json --seed 999
python main.py --config ./config/generator.json --output D:/xxx/Generated
```

### 参数说明

| 参数 | 说明 |
|---|---|
| --config | 主配置文件路径 |
| --language | 覆盖配置中的语言 |
| --seed | 覆盖随机种子 |
| --output | 覆盖输出目录 |

---

## 17. Batch 启动脚本设计

示例 `run.bat`：

```bat
@echo off
python main.py --config .\config\generator.json
pause
```

---

## 18. Unity 集成建议

## 18.1 推荐方式
通过 Unity Editor C# 菜单调用 Python 生成器：

1. Unity 菜单项触发
2. 调用外部 Python 脚本
3. 生成文件到 `Assets/Plugins/iOS/Generated/`
4. 执行 `AssetDatabase.Refresh()`

## 18.2 典型流程
```txt
Unity Editor Menu
   -> Run Python Generator
   -> Write iOS Native Files
   -> Refresh Assets
   -> Build iOS
```

---

## 19. 开发阶段规划

## 19.1 V1 最小可用版本
包含：
- JSON 配置读取
- Objective-C 生成
- C++ 生成
- 命名去重
- 状态文件
- 行数控制基础能力

## 19.2 V2 增强版本
包含：
- 模板可配置
- 方法体复杂度增强
- 批量配置执行
- Unity Editor 菜单调用

## 19.3 V3 扩展版本
包含：
- `.mm` 桥接层
- C 接口桥接导出
- GUI 配置工具

---

## 20. 测试方案

## 20.1 单元测试
测试模块：
- 配置加载
- 命名生成
- 冲突处理
- 状态读写
- 行数预算

## 20.2 集成测试
测试场景：
- 生成 Objective-C 类
- 生成 C++ 类
- 增量生成
- 重复执行
- 输出到 Unity 工程目录

## 20.3 人工验证
验证项：
- 文件结构是否正确
- 命名是否符合规则
- 代码是否可编译
- 行数是否落在范围内

---

## 21. 风险与应对

## 21.1 风险：词库组合不足
应对：
- 提前计算组合上限
- 配置校验时提示风险

## 21.2 风险：总行数难以精准命中
应对：
- 允许范围控制而非精确值
- 使用注释/空行/辅助方法微调

## 21.3 风险：Unity 工程路径差异
应对：
- 目录完全配置化
- 提供命令行覆盖能力

## 21.4 风险：状态文件长期膨胀
应对：
- 状态分层
- 支持归档与清理

---

## 22. 最终推荐实施方案

### 技术栈
- 语言：Python 3
- 配置：JSON
- 状态：JSON
- 启动：CLI + Batch
- 可选集成：Unity Editor C# 调用

### 原则
- 配置驱动
- 模板生成
- 命名唯一
- 增量可追踪
- 输出可直接落地到 Unity iOS Plugin 目录

---

## 23. 下一步实施内容

下一步进入代码实现阶段时，建议直接输出以下内容：

1. `main.py`
2. `config/generator.json`
3. `config/vocabulary.json`
4. `config/state.json`
5. `core/config_loader.py`
6. `core/state_store.py`
7. `core/name_builder.py`
8. `core/line_budget.py`
9. `core/file_writer.py`
10. `core/objc_generator.py`
11. `core/cpp_generator.py`
12. `run.bat`

---