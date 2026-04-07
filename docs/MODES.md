# iOS 插件代码生成器 - 四种生成模式详解

本文档详细说明 iOS 插件代码生成器支持的 4 种生成模式及其配置方式。

## 目录

- [四种生成模式概述](#四种生成模式概述)
- [模式 1: OC 代码生成](#模式 1-oc-代码生成)
- [模式 2: OC String 生成](#模式 2-oc-string-生成)
- [模式 3: C++ 代码生成](#模式 3-c-代码生成)
- [模式 4: C++ String 生成](#模式 4-c-string-生成)
- [代码多样性说明](#代码多样性说明)
- [配置示例](#配置示例)
- [使用示例](#使用示例)

---

## 四种生成模式概述

| 模式 | 语言 | 输出内容 | 文件扩展名 |
|------|------|----------|-----------|
| **OC 代码生成** | Objective-C | 类/方法/属性 | `.h` / `.m` |
| **OC String 生成** | Objective-C | String 常量 | `.m` |
| **C++ 代码生成** | C++ | 类/方法/成员变量 | `.hpp` / `.cpp` |
| **C++ String 生成** | C++ | `const char[]` 常量 | `.cpp` |

---

## 模式 1: OC 代码生成

### 配置方式

```json
{
  "language": "objc"
}
```

### 特点

- 生成完整的 Objective-C 类，包含属性、方法
- 输出 `.h` 头文件和 `.m` 实现文件
- 支持 15 种方法模板，8 类代码块
- 支持多种返回类型和参数类型
- 支持生成 `ABPluginRegistry.m` 统一调用所有类

### 方法模板

支持以下 15 种方法模板类型：

| 模板类型 | 说明 |
|----------|------|
| `simple` | 简单方法，直接返回 |
| `validation` | 包含参数验证逻辑 |
| `cache` | 包含缓存检查逻辑 |
| `async` | 包含异步回调逻辑 |
| `log` | 包含日志输出逻辑 |
| `transform` | 包含数据转换逻辑 |
| `factory` | 工厂方法，创建并返回对象 |
| `singleton` | 单例模式方法 |
| `delegate` | 代理模式方法 |
| `notification` | 通知中心相关方法 |
| `kvo` | KVO 相关方法 |
| `block` | 包含 Block 回调的方法 |
| `property_chain` | 属性链式调用 |
| `computed` | 计算型属性访问器 |
| `lazy` | 懒加载方法 |

### 代码块类型

| 代码块 | 说明 |
|--------|------|
| `log` | NSLog 日志输出 |
| `validation` | 参数有效性检查 |
| `cache` | 缓存读取/写入 |
| `async` | 异步执行块 |
| `transform` | 数据格式转换 |
| `error_handling` | 错误处理逻辑 |
| `memory_management` | 内存管理相关 |
| `state_check` | 状态检查逻辑 |

### 返回类型

- **基本类型**: `NSInteger`, `NSUInteger`, `BOOL`, `float`, `double`
- **对象类型**: `NSString *`, `NSArray *`, `NSDictionary *`, `NSData *`
- **指针类型**: `void *`, `const void *`

### 参数类型

- **基本类型**: `NSInteger`, `NSUInteger`, `BOOL`, `float`, `double`
- **对象类型**: `NSString *`, `NSArray *`, `NSDictionary *`, `NSData *`
- **Block 类型**: `void (^)(NSString *result)`, `void (^)(BOOL success)`

### 输出示例

**头文件 (`ABDataCacheManager.h`)**:
```objc
#import <Foundation/Foundation.h>

@interface ABDataCacheManager : NSObject

@property (nonatomic, assign) NSInteger cachedCount;
@property (nonatomic, strong) NSString *activeState;

- (void)loadCacheIfNeeded;
- (NSInteger)buildSignalForIndex:(NSInteger)index;
- (NSString *)fetchDataWithOptions:(NSDictionary *)options;

@end
```

**实现文件 (`ABDataCacheManager.m`)**:
```objc
#import "ABDataCacheManager.h"

@implementation ABDataCacheManager

- (instancetype)init {
    self = [super init];
    if (self) {
        _cachedCount = 0;
        _activeState = @"initial";
    }
    return self;
}

- (void)loadCacheIfNeeded {
    if (self.cachedCount > 0) {
        NSLog(@"[ABDataCacheManager] Cache already loaded.");
        return;
    }
    // Load cache logic
    self.cachedCount = 100;
}

- (NSInteger)buildSignalForIndex:(NSInteger)index {
    if (index < 0) {
        return -1;
    }
    return index * 2;
}

@end
```

---

## 模式 2: OC String 生成

### 配置方式

```json
{
  "language": "string",
  "stringLanguage": "objc"
}
```

### 特点

- 生成单个文件包含多个 String 常量
- 支持 `word`（词汇组合）和 `sentence`（句子）两种模式
- 自动生成 `ABPrintStringConstants()` 函数
- 输出 `.m` 文件

### String 模式

| 模式 | 说明 | 示例 |
|------|------|------|
| `word` | 词汇组合模式 | `"Data Cache Manager"` |
| `sentence` | 句子模式 | `"The quick brown fox jumps over the lazy dog."` |

### 输出示例

**词汇模式 (`ABStringConstants.m`)**:
```objc
#import <Foundation/Foundation.h>

static NSString * const ABStringConstant_0 = @"Data Cache Manager";
static NSString * const ABStringConstant_1 = @"Fast Signal Handler";
static NSString * const ABStringConstant_2 = @"Core Vector Builder";
static NSString * const ABStringConstant_3 = @"Rapid Pixel Service";

void ABPrintStringConstants() {
    if (YES) return;
    NSLog(@"%@", ABStringConstant_0);
    NSLog(@"%@", ABStringConstant_1);
    NSLog(@"%@", ABStringConstant_2);
    NSLog(@"%@", ABStringConstant_3);
}
```

**句子模式 (`ABStringConstants.m`)**:
```objc
#import <Foundation/Foundation.h>

static NSString * const ABStringConstant_0 = @"The quick brown fox jumps over the lazy dog.";
static NSString * const ABStringConstant_1 = @"A journey of a thousand miles begins with a single step.";
static NSString * const ABStringConstant_2 = @"To be or not to be, that is the question.";

void ABPrintStringConstants() {
    if (YES) return;
    NSLog(@"%@", ABStringConstant_0);
    NSLog(@"%@", ABStringConstant_1);
    NSLog(@"%@", ABStringConstant_2);
}
```

---

## 模式 3: C++ 代码生成

### 配置方式

```json
{
  "language": "cpp"
}
```

### 特点

- 生成完整的 C++ 类，使用纯 C++ 语法
- 输出 `.hpp` 头文件和 `.cpp` 实现文件
- 支持 21 种 C++ 方法模板，11 类 C++ 代码块
- 支持生成 `ABPluginRegistry.cpp` 统一调用所有类

### 方法模板

支持以下 21 种 C++ 方法模板类型：

| 模板类型 | 说明 |
|----------|------|
| `constructor` | 构造函数 |
| `destructor` | 析构函数 |
| `getter` | 成员变量 getter |
| `setter` | 成员变量 setter |
| `simple` | 简单方法 |
| `validation` | 参数验证方法 |
| `cache` | 缓存相关方法 |
| `factory` | 工厂方法 |
| `singleton` | 单例模式方法 |
| `observer` | 观察者模式方法 |
| `strategy` | 策略模式方法 |
| `builder` | 构建者模式方法 |
| `adapter` | 适配器模式方法 |
| `decorator` | 装饰器模式方法 |
| `facade` | 外观模式方法 |
| `proxy` | 代理模式方法 |
| `command` | 命令模式方法 |
| `iterator` | 迭代器模式方法 |
| `template_method` | 模板方法模式 |
| `state` | 状态模式方法 |
| `visitor` | 访问者模式方法 |

### 代码块类型

| 代码块 | 说明 |
|--------|------|
| `log` | std::cout 日志输出 |
| `validation` | 参数有效性检查 |
| `cache` | 缓存读取/写入 |
| `transform` | 数据格式转换 |
| `error_handling` | 异常处理逻辑 |
| `memory_management` | 智能指针管理 |
| `state_check` | 状态检查逻辑 |
| `lock` | 锁相关逻辑 |
| `thread` | 线程相关逻辑 |
| `file_io` | 文件读写逻辑 |
| `network` | 网络相关逻辑 |

### 返回类型

- **基本类型**: `int`, `unsigned int`, `bool`, `float`, `double`, `size_t`
- **对象类型**: `std::string`, `std::vector<T>`, `std::map<K,V>`, `std::unique_ptr<T>`
- **指针类型**: `void*`, `const void*`, `T*`

### 参数类型

- **值类型**: `int`, `bool`, `float`, `double`
- **引用类型**: `const std::string&`, `std::vector<int>&`
- **指针类型**: `const char*`, `void*`

### 输出示例

**头文件 (`ABDataCacheManager.hpp`)**:
```cpp
#pragma once

#include <string>
#include <vector>
#include <memory>

class ABDataCacheManager {
public:
    ABDataCacheManager();
    ~ABDataCacheManager();
    
    void loadCacheIfNeeded();
    int buildSignalForIndex(int index);
    std::string fetchDataWithOptions(const std::map<std::string, std::string>& options);
    
    int getCachedCount() const;
    void setCachedCount(int count);
    
private:
    int cachedCount;
    std::string activeState;
    std::vector<std::string> cacheData;
};
```

**实现文件 (`ABDataCacheManager.cpp`)**:
```cpp
#include "ABDataCacheManager.hpp"
#include <iostream>

ABDataCacheManager::ABDataCacheManager() 
    : cachedCount(0), activeState("initial") {
}

ABDataCacheManager::~ABDataCacheManager() {
    cacheData.clear();
}

void ABDataCacheManager::loadCacheIfNeeded() {
    if (cachedCount > 0) {
        std::cout << "[ABDataCacheManager] Cache already loaded." << std::endl;
        return;
    }
    // Load cache logic
    cachedCount = 100;
}

int ABDataCacheManager::buildSignalForIndex(int index) {
    if (index < 0) {
        return -1;
    }
    return index * 2;
}

std::string ABDataCacheManager::fetchDataWithOptions(
    const std::map<std::string, std::string>& options) {
    std::string result = "default";
    auto it = options.find("key");
    if (it != options.end()) {
        result = it->second;
    }
    return result;
}

int ABDataCacheManager::getCachedCount() const {
    return cachedCount;
}

void ABDataCacheManager::setCachedCount(int count) {
    cachedCount = count;
}
```

---

## 模式 4: C++ String 生成

### 配置方式

```json
{
  "language": "string",
  "stringLanguage": "cpp"
}
```

### 特点

- 生成单个文件包含多个 `const char[]` 常量
- 支持 `word`（词汇组合）和 `sentence`（句子）两种模式
- 自动生成 `ABPrintStringConstants()` 函数
- 输出 `.cpp` 文件

### String 模式

| 模式 | 说明 | 示例 |
|------|------|------|
| `word` | 词汇组合模式 | `"Data Cache Manager"` |
| `sentence` | 句子模式 | `"The quick brown fox jumps over the lazy dog."` |

### 输出示例

**词汇模式 (`ABStringConstants.cpp`)**:
```cpp
#include <cstdio>

static const char ABStringConstant_0[] = "Data Cache Manager";
static const char ABStringConstant_1[] = "Fast Signal Handler";
static const char ABStringConstant_2[] = "Core Vector Builder";
static const char ABStringConstant_3[] = "Rapid Pixel Service";

void ABPrintStringConstants() {
    if (true) return;
    printf("%s\n", ABStringConstant_0);
    printf("%s\n", ABStringConstant_1);
    printf("%s\n", ABStringConstant_2);
    printf("%s\n", ABStringConstant_3);
}
```

**句子模式 (`ABStringConstants.cpp`)**:
```cpp
#include <cstdio>

static const char ABStringConstant_0[] = "The quick brown fox jumps over the lazy dog.";
static const char ABStringConstant_1[] = "A journey of a thousand miles begins with a single step.";
static const char ABStringConstant_2[] = "To be or not to be, that is the question.";

void ABPrintStringConstants() {
    if (true) return;
    printf("%s\n", ABStringConstant_0);
    printf("%s\n", ABStringConstant_1);
    printf("%s\n", ABStringConstant_2);
}
```

---

## 代码多样性说明

### 类内多样性

每个生成的类内部包含多种变化：

- **方法模板多样性**: 每个类使用 5-8 种不同的方法模板
- **返回类型多样性**: 方法有不同的返回类型（基本类型、对象类型、指针类型）
- **参数类型多样性**: 方法有不同的参数类型和数量（0-4 个参数）
- **代码块多样性**: 方法实现使用不同的代码块组合（log、validation、cache、async 等）

### 类间多样性

不同类之间包含多种变化：

- **类类型多样性**: 不同类类型使用不同的方法组合
  - Manager 类：侧重缓存、状态管理方法
  - Service 类：侧重数据处理、业务逻辑方法
  - Factory 类：侧重对象创建、工厂方法
  - Handler 类：侧重事件处理、回调方法
  - Builder 类：侧重构建、组装方法
  - Store 类：侧重数据存储、检索方法

- **命名多样性**: 类名使用不同的词库组合
  - 380 个前缀 × 310 个中间词 × 300 个后缀 = **35,340,000 种组合**

- **成员变量多样性**: 成员变量类型和数量不同
  - 基本类型变量：int, bool, float
  - 对象类型变量：std::string, std::vector, std::map
  - 指针类型变量：raw pointer, smart pointer

### 方法调用链

- **内部调用**: 部分方法调用类内其他方法形成调用链
- **跨类调用**: 注册表模式统一初始化所有类
- **顶层覆盖**: 确保顶层调用能引用到所有生成的代码

### 注册表统一入口

注册表文件统一调用所有生成的类，确保代码被完整引用：

**Objective-C 注册表 (`ABPluginRegistry.m`)**:
```objc
void ABInitializeAllPlugins() {
    if (ABPluginsInitialized) return;
    ABPluginsInitialized = YES;
    
    // 实例化并调用所有类
    ABDataCacheManager *m1 = [[ABDataCacheManager alloc] init];
    [m1 loadData];
    
    ABSignalHandler *m2 = [[ABSignalHandler alloc] init];
    [m2 processSignal];
    
    // ... 所有类
}
```

**C++ 注册表 (`ABPluginRegistry.cpp`)**:
```cpp
extern "C" {
    void ABInitializeAllPlugins() {
        if (g_ABPluginsInitialized) return;
        g_ABPluginsInitialized = true;
        
        // 实例化并调用所有类
        ABDataCacheManager* m1 = new ABDataCacheManager();
        m1->loadData();
        delete m1;
        
        ABSignalHandler* m2 = new ABSignalHandler();
        m2->processSignal();
        delete m2;
        
        // ... 所有类
    }
}
```

---

## 配置示例

### 配置 1: OC 代码生成

```json
{
  "language": "objc",
  "outputDir": "./output_objc",
  "classCount": 10,
  "totalLineRange": [500, 1500],
  "linesPerClassRange": [80, 200],
  "methodsPerClassRange": [5, 12],
  "propertiesPerClassRange": [2, 6],
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

### 配置 2: OC String 生成

```json
{
  "language": "string",
  "outputDir": "./output_string_objc",
  "stringCount": 1000,
  "stringMode": "word",
  "stringLanguage": "objc",
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true
}
```

### 配置 3: C++ 代码生成

```json
{
  "language": "cpp",
  "outputDir": "./output_cpp",
  "classCount": 10,
  "totalLineRange": [600, 1800],
  "linesPerClassRange": [100, 250],
  "methodsPerClassRange": [6, 15],
  "propertiesPerClassRange": [3, 8],
  "classPrefix": "AB",
  "incremental": true,
  "overwrite": false,
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true,
  "generateRegistry": true,
  "registryLanguage": "cpp"
}
```

### 配置 4: C++ String 生成

```json
{
  "language": "string",
  "outputDir": "./output_string_cpp",
  "stringCount": 500,
  "stringMode": "sentence",
  "stringLanguage": "cpp",
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true
}
```

---

## 使用示例

### 示例 1: OC 代码生成

**步骤 1: 创建配置文件**

创建 `config/generator_objc.json`:
```json
{
  "language": "objc",
  "outputDir": "./output_objc",
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

**步骤 2: 运行生成器**

```bash
python main.py --config ./config/generator_objc.json
```

**步骤 3: 查看输出**

```
output_objc/
├── ABDataCacheManager.h
├── ABDataCacheManager.m
├── ABSignalHandler.h
├── ABSignalHandler.m
├── ABVectorBuilder.h
├── ABVectorBuilder.m
├── ABPluginRegistry.h
└── ABPluginRegistry.m
```

**步骤 4: 查看统计报告**

```
========================================
代码行数统计报告
========================================
目标目录：./output_objc

文件统计:
  总文件数：14
  .h 文件：7
  .m 文件：7

行数统计:
  总行数：842
  代码行数：650
  空行数：120
  注释行数：72
```

---

### 示例 2: OC String 生成

**步骤 1: 创建配置文件**

创建 `config/generator_string_objc.json`:
```json
{
  "language": "string",
  "outputDir": "./output_string_objc",
  "stringCount": 1000,
  "stringMode": "word",
  "stringLanguage": "objc",
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true
}
```

**步骤 2: 运行生成器**

```bash
python main.py --config ./config/generator_string_objc.json
```

**步骤 3: 查看输出**

```
output_string_objc/
└── ABStringConstants.m
```

**步骤 4: 查看生成内容**

```objc
#import <Foundation/Foundation.h>

static NSString * const ABStringConstant_0 = @"Data Cache Manager";
static NSString * const ABStringConstant_1 = @"Fast Signal Handler";
// ... 共 1000 个常量

void ABPrintStringConstants() {
    if (YES) return;
    NSLog(@"%@", ABStringConstant_0);
    NSLog(@"%@", ABStringConstant_1);
    // ... 打印所有常量
}
```

---

### 示例 3: C++ 代码生成

**步骤 1: 创建配置文件**

创建 `config/generator_cpp.json`:
```json
{
  "language": "cpp",
  "outputDir": "./output_cpp",
  "classCount": 8,
  "totalLineRange": [800, 2000],
  "linesPerClassRange": [100, 250],
  "methodsPerClassRange": [6, 15],
  "propertiesPerClassRange": [3, 8],
  "classPrefix": "AB",
  "incremental": true,
  "overwrite": false,
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true,
  "generateRegistry": true,
  "registryLanguage": "cpp"
}
```

**步骤 2: 运行生成器**

```bash
python main.py --config ./config/generator_cpp.json
```

**步骤 3: 查看输出**

```
output_cpp/
├── ABDataCacheManager.hpp
├── ABDataCacheManager.cpp
├── ABSignalHandler.hpp
├── ABSignalHandler.cpp
├── ABVectorBuilder.hpp
├── ABVectorBuilder.cpp
├── ABPluginRegistry.cpp
```

**步骤 4: 查看统计报告**

```
========================================
代码行数统计报告
========================================
目标目录：./output_cpp

文件统计:
  总文件数：17
  .hpp 文件：8
  .cpp 文件：9

行数统计:
  总行数：1250
  代码行数：980
  空行数：180
  注释行数：90
```

---

### 示例 4: C++ String 生成

**步骤 1: 创建配置文件**

创建 `config/generator_string_cpp.json`:
```json
{
  "language": "string",
  "outputDir": "./output_string_cpp",
  "stringCount": 500,
  "stringMode": "sentence",
  "stringLanguage": "cpp",
  "randomSeed": 12345,
  "stateFile": "./config/state.json",
  "vocabularyFile": "./config/vocabulary.json",
  "showStats": true
}
```

**步骤 2: 运行生成器**

```bash
python main.py --config ./config/generator_string_cpp.json
```

**步骤 3: 查看输出**

```
output_string_cpp/
└── ABStringConstants.cpp
```

**步骤 4: 查看生成内容**

```cpp
#include <cstdio>

static const char ABStringConstant_0[] = "The quick brown fox jumps over the lazy dog.";
static const char ABStringConstant_1[] = "A journey of a thousand miles begins with a single step.";
// ... 共 500 个常量

void ABPrintStringConstants() {
    if (true) return;
    printf("%s\n", ABStringConstant_0);
    printf("%s\n", ABStringConstant_1);
    // ... 打印所有常量
}
```

---

## 命令行参数覆盖

所有模式都支持使用命令行参数覆盖配置：

```bash
# 覆盖语言选项
python main.py --config ./config/generator.json --language cpp

# 覆盖输出目录
python main.py --config ./config/generator.json --output ./output/custom

# 覆盖随机种子
python main.py --config ./config/generator.json --seed 42

# 组合使用
python main.py --config ./config/generator.json --language cpp --seed 42 --output ./output/cpp_test
```

---

## 相关文档

- [项目总览](../ReadMe.md)
- [Unity 集成说明](unity_integration.md)
- [词库配置](../config/vocabulary.json)

---

*文档最后更新：2026-04-07*
