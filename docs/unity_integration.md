# Unity iOS 插件集成说明

本文档说明如何在 Unity 项目中集成和使用由 IOSPluginCodeGenerator 生成的 C++ 和 Objective-C 代码。

## 0. 统一入口注册表（新增）

### 0.1 功能说明

从版本 v2.0 开始，生成器支持自动生成统一入口注册表文件，用于批量初始化和清理所有生成的插件类。

### 0.2 启用方式

在 `generator.json` 配置文件中添加：

```json
{
  "generateRegistry": true,      // 是否生成统一入口注册表
  "registryLanguage": "objc"     // 注册表语言：objc 或 cpp
}
```

### 0.3 生成的文件

| 文件 | 说明 |
|------|------|
| `ABPluginRegistry.h` | 头文件，声明 `ABInitializeAllPlugins()` 和 `ABCleanupAllPlugins()` 函数 |
| `ABPluginRegistry.m` | Objective-C 实现文件 |
| `ABPluginRegistry.cpp` | C++ 实现文件 |

### 0.4 使用 C# 包装类

项目提供了完整的 C# 包装类模板 [`docs/PluginWrapper.cs`](PluginWrapper.cs)，包含：

- `ABPluginWrapper` 类：封装原生调用
- `ABPluginAutoInitializer` 类：自动初始化 MonoBehavior

**使用方法：**

1. 将 `PluginWrapper.cs` 复制到 Unity 项目的 `Assets/Scripts/` 目录
2. 在场景中添加 `ABPluginAutoInitializer` 组件到 GameObject
3. 或在代码中手动调用：

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

### 0.5 手动集成

如果不想使用包装类，可以手动声明原生方法：

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

public class ABPluginManager
{
    [DllImport("__Internal")]
    private static extern void ABInitializeAllPlugins();
    
    [DllImport("__Internal")]
    private static extern void ABCleanupAllPlugins();
    
    public static void Initialize()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABInitializeAllPlugins();
        #endif
    }
    
    public static void Cleanup()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABCleanupAllPlugins();
        #endif
    }
}
```

---

## 1. Unity 项目结构

将生成的代码文件放入 Unity 项目的以下目录结构中：

```
UnityProject/
└── Assets/
    └── Plugins/
        └── iOS/
            ├── ABDataCacheManager.h
            ├── ABDataCacheManager.m
            ├── ABStringConstants.h
            ├── ABStringConstants.m
            ├── ABStringConstants.cpp
            └── ...
```

### 目录说明

| 目录 | 说明 |
|------|------|
| `Assets/Plugins/iOS/` | 存放 iOS 原生插件代码，Unity 会在 iOS 构建时自动包含这些文件 |

### 文件类型说明

- **`.h` 文件**：Objective-C/C++ 头文件，声明函数和接口
- **`.m` 文件**：Objective-C 实现文件
- **`.cpp` 文件**：C++ 实现文件

---

## 2. 普通代码生成模式（类/方法/属性）

本节说明由 IOSPluginCodeGenerator 生成的普通 Objective-C 类（包含类定义、属性、方法）在 Unity 中的调用方式。

### 2.1 生成的代码结构说明

普通模式生成的代码包含以下元素：

| 元素类型 | Objective-C 语法 | 说明 |
|----------|------------------|------|
| **类定义** | `@interface ClassName : NSObject` / `@implementation` | 声明和实现一个类 |
| **属性** | `@property (nonatomic, strong) Type *name;` | 类的成员变量 |
| **实例方法** | `- (returnType)methodName:(paramType)param;` | 需要实例化后调用的方法 |
| **类方法** | `+ (returnType)methodName:(paramType)param;` | 直接通过类名调用的静态方法 |

### 2.2 生成的 OC 代码示例

```objc
// ABDataCacheManager.h
#import <Foundation/Foundation.h>

@interface ABDataCacheManager : NSObject

@property (nonatomic, strong) NSString *cacheKey;

- (instancetype)initWithCacheKey:(NSString *)key;
- (void)loadData;
- (NSString *)getData;
+ (void)clearAllCache;

@end
```

```objc
// ABDataCacheManager.m
#import "ABDataCacheManager.h"

@implementation ABDataCacheManager {
    NSString *_data;
}

@synthesize cacheKey = _cacheKey;

- (instancetype)initWithCacheKey:(NSString *)key {
    self = [super init];
    if (self) {
        _cacheKey = [key copy];
        _data = @"";
    }
    return self;
}

- (void)loadData {
    // 模拟数据加载
    _data = [NSString stringWithFormat:@"Data for key: %@", _cacheKey];
}

- (NSString *)getData {
    return _data;
}

+ (void)clearAllCache {
    // 清理所有缓存数据
    NSLog(@"Clearing all cache");
}

@end
```

### 2.3 工厂函数模式（Unity 调用必需）

为了让 Unity C# 代码能够调用 Objective-C 类，需要在 `.m` 文件中添加工厂函数。这些函数使用 `extern "C"` 声明，以便 C# 通过 `DllImport` 调用。

在 `ABDataCacheManager.m` 文件末尾添加：

```objc
// 在 .m 文件末尾添加
#ifdef UNITY_PLUGIN
extern "C" {
    ABDataCacheManager* ABDataCacheManager_Create(const char* key) {
        return [[ABDataCacheManager alloc] initWithCacheKey:[NSString stringWithUTF8String:key]];
    }
    
    void ABDataCacheManager_Destroy(ABDataCacheManager* obj) {
        [obj release];
    }
    
    void ABDataCacheManager_LoadData(ABDataCacheManager* obj) {
        [obj loadData];
    }
    
    const char* ABDataCacheManager_GetData(ABDataCacheManager* obj) {
        return [[obj getData] UTF8String];
    }
    
    void ABDataCacheManager_ClearAllCache() {
        [ABDataCacheManager clearAllCache];
    }
}
#endif
```

#### 工厂函数命名规则

| 函数类型 | 命名格式 | 示例 |
|----------|----------|------|
| **构造函数** | `ClassName_Create` | `ABDataCacheManager_Create` |
| **析构函数** | `ClassName_Destroy` | `ABDataCacheManager_Destroy` |
| **实例方法** | `ClassName_MethodName` | `ABDataCacheManager_LoadData` |
| **类方法** | `ClassName_MethodName` | `ABDataCacheManager_ClearAllCache` |

### 2.4 C# 包装类

在 Unity 中创建 C# 包装类来封装原生调用：

```csharp
using System;
using System.Runtime.InteropServices;
using UnityEngine;

public class ABDataCacheManagerWrapper : IDisposable
{
    private System.IntPtr nativePtr;
    
    #region Native Methods
    
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
    
    #endregion
    
    #region Constructor & Destructor
    
    public ABDataCacheManagerWrapper(string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        nativePtr = ABDataCacheManager_Create(key);
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
    
    ~ABDataCacheManagerWrapper()
    {
        Dispose();
    }
    
    #endregion
    
    #region Public API
    
    public void LoadData()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        if (nativePtr != System.IntPtr.Zero)
        {
            ABDataCacheManager_LoadData(nativePtr);
        }
        #endif
    }
    
    public string GetData()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        if (nativePtr != System.IntPtr.Zero)
        {
            System.IntPtr ptr = ABDataCacheManager_GetData(nativePtr);
            return Marshal.PtrToStringAnsi(ptr);
        }
        #endif
        return string.Empty;
    }
    
    public static void ClearAllCache()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_ClearAllCache();
        #endif
    }
    
    #endregion
}
```

### 2.5 完整调用流程示例

```csharp
using UnityEngine;

public class TestCacheManager : MonoBehaviour
{
    void Start()
    {
        // 创建实例
        var cacheManager = new ABDataCacheManagerWrapper("myCache");
        
        // 调用实例方法
        cacheManager.LoadData();
        string data = cacheManager.GetData();
        Debug.Log($"Loaded data: {data}");
        
        // 调用类方法
        ABDataCacheManagerWrapper.ClearAllCache();
        
        // 释放资源
        cacheManager.Dispose();
    }
}
```

### 2.6 批量生成类的调用说明

当使用 IOSPluginCodeGenerator 批量生成大量类（如 8000 个类）时，不需要全部调用。建议：

1. **选择示例类进行测试**：选择 1-2 个有代表性的类进行完整调用测试
2. **按需调用**：根据实际业务需求选择需要调用的类
3. **分类管理**：将功能相似的类分组，每组选择一个代表类

#### 示例：从批量生成的类中选择调用

```csharp
// 假设有 8000 个生成的类，只需要调用其中几个
public class PluginManager : MonoBehaviour
{
    private ABDataCacheManagerWrapper _cacheManager;
    
    void Start()
    {
        // 只调用需要的类
        _cacheManager = new ABDataCacheManagerWrapper("userCache");
        _cacheManager.LoadData();
        
        // 其他 7999 个类不需要全部实例化
        // 根据业务需要选择性调用
    }
    
    void OnDestroy()
    {
        _cacheManager?.Dispose();
    }
}
```

---

## 3. Objective-C 代码调用（函数模式）

### 3.1 C# 端声明

在 Unity 中创建 C# 包装类来调用 Objective-C 代码：

```csharp
using System.Runtime.InteropServices;

public class iOSPluginWrapper
{
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern void ABPrintStringConstants();
    #endif
    
    public static void PrintStringConstants()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABPrintStringConstants();
        #endif
    }
}
```

### 3.2 使用示例

```csharp
using UnityEngine;

public class TestPlugin : MonoBehaviour
{
    void Start()
    {
        // 调用 Objective-C 插件方法
        iOSPluginWrapper.PrintStringConstants();
    }
}
```

### 3.3 完整的 Objective-C 代码示例

生成的 Objective-C 代码示例（`ABStringConstants.m`）：

```objectivec
#import <Foundation/Foundation.h>

// 打印字符串常量
extern void ABPrintStringConstants() {
    NSLog(@"String Constants:");
    NSLog(@"kABGreeting = %@", @"Hello");
    NSLog(@"kABFarewell = %@", @"Goodbye");
}

// 获取字符串常量值
extern const NSString* ABGetStringConstant(NSString* key) {
    if ([key isEqualToString:@"kABGreeting"]) {
        return @"Hello";
    }
    if ([key isEqualToString:@"kABFarewell"]) {
        return @"Goodbye";
    }
    return nil;
}
```

---

## 4. C++ 代码调用

### 4.1 C# 端声明

C++ 代码需要使用 `extern "C"` 包装以支持 C# 调用：

```csharp
using System.Runtime.InteropServices;

public class CPPPluginWrapper
{
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("ABStringConstants")]
    private static extern void ABPrintStringConstants();
    #endif
    
    public static void PrintStringConstants()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABPrintStringConstants();
        #endif
    }
}
```

### 4.2 C++ 代码示例

生成的 C++ 代码示例（`ABStringConstants.cpp`）：

```cpp
#include <iostream>
#include <string>

extern "C" {
    void ABPrintStringConstants() {
        std::cout << "String Constants:" << std::endl;
        std::cout << "kABGreeting = " << "Hello" << std::endl;
        std::cout << "kABFarewell = " << "Goodbye" << std::endl;
    }
    
    const char* ABGetStringConstant(const char* key) {
        if (std::string(key) == "kABGreeting") {
            return "Hello";
        }
        if (std::string(key) == "kABFarewell") {
            return "Goodbye";
        }
        return "";
    }
}
```

---

## 5. 完整示例

### 示例 1：调用 String 常量打印

#### Objective-C 代码（`ABStringConstants.m`）

```objectivec
#import <Foundation/Foundation.h>

extern void ABPrintStringConstants() {
    NSLog(@"=== String Constants ===");
    NSLog(@"kABGreeting = %@", @"Hello");
    NSLog(@"kABFarewell = %@", @"Goodbye");
    NSLog(@"kABWelcome = %@", @"Welcome");
}
```

#### C# 包装类

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

public class StringConstantsPlugin
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
        Debug.Log("[iOS Plugin] Running in Editor - skipping native call");
        #endif
    }
}
```

#### 使用示例

```csharp
using UnityEngine;

public class TestStringConstants : MonoBehaviour
{
    void Start()
    {
        StringConstantsPlugin.PrintConstants();
    }
}
```

---

### 示例 2：访问 String 常量值

#### Objective-C 代码（返回 const NSString*）

```objectivec
#import <Foundation/Foundation.h>

extern const NSString* ABGetStringConstant(const char* key) {
    NSString* keyStr = [NSString stringWithUTF8String:key];
    
    if ([keyStr isEqualToString:@"kABGreeting"]) {
        return @"Hello";
    }
    if ([keyStr isEqualToString:@"kABFarewell"]) {
        return @"Goodbye";
    }
    if ([keyStr isEqualToString:@"kABWelcome"]) {
        return @"Welcome";
    }
    
    return @"";
}

extern const char* ABGetStringConstantUTF8(const char* key) {
    return [ABGetStringConstant(key) UTF8String];
}
```

#### C# 包装类（返回 string）

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

public class StringConstantsReader
{
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern System.IntPtr ABGetStringConstantUTF8(string key);
    #endif
    
    public static string GetConstant(string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        System.IntPtr ptr = ABGetStringConstantUTF8(key);
        return Marshal.PtrToStringAnsi(ptr);
        #else
        Debug.Log($"[iOS Plugin] Editor mode - returning empty for key: {key}");
        return string.Empty;
        #endif
    }
}
```

#### 使用示例

```csharp
using UnityEngine;

public class TestStringReader : MonoBehaviour
{
    void Start()
    {
        string greeting = StringConstantsReader.GetConstant("kABGreeting");
        string farewell = StringConstantsReader.GetConstant("kABFarewell");
        
        Debug.Log($"Greeting: {greeting}");
        Debug.Log($"Farewell: {farewell}");
    }
}
```

---

### 示例 3：批量生成类的调用

#### 生成的 Objective-C 代码

```objectivec
// ABDataCacheManager.h
#import <Foundation/Foundation.h>

@interface ABDataCacheManager : NSObject
+ (void)cacheString:(NSString *)value forKey:(NSString *)key;
+ (NSString *)getCachedStringForKey:(NSString *)key;
+ (void)clearCache;
@end

// ABDataCacheManager.m
#import "ABDataCacheManager.h"

static NSMutableDictionary* _cache = nil;

@implementation ABDataCacheManager

+ (void)initialize {
    if (self == [ABDataCacheManager class]) {
        _cache = [[NSMutableDictionary alloc] init];
    }
}

+ (void)cacheString:(NSString *)value forKey:(NSString *)key {
    @synchronized(_cache) {
        [_cache setObject:value forKey:key];
    }
}

+ (NSString *)getCachedStringForKey:(NSString *)key {
    @synchronized(_cache) {
        return [_cache objectForKey:key];
    }
}

+ (void)clearCache {
    @synchronized(_cache) {
        [_cache removeAllObjects];
    }
}

@end
```

#### C# 包装类

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

public class DataCacheManager
{
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_cacheString(string value, string key);
    
    [DllImport("__Internal")]
    private static extern System.IntPtr ABDataCacheManager_getCachedStringForKey(string key);
    
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_clearCache();
    #endif
    
    public static void CacheString(string value, string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_cacheString(value, key);
        #endif
    }
    
    public static string GetCachedString(string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        System.IntPtr ptr = ABDataCacheManager_getCachedStringForKey(key);
        return Marshal.PtrToStringAnsi(ptr);
        #else
        return string.Empty;
        #endif
    }
    
    public static void ClearCache()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_clearCache();
        #endif
    }
}
```

#### 使用示例

```csharp
using UnityEngine;

public class TestDataCache : MonoBehaviour
{
    void Start()
    {
        // 缓存数据
        DataCacheManager.CacheString("Hello World", "greeting");
        DataCacheManager.CacheString("Goodbye World", "farewell");
        
        // 读取缓存
        string greeting = DataCacheManager.GetCachedString("greeting");
        string farewell = DataCacheManager.GetCachedString("farewell");
        
        Debug.Log($"Cached greeting: {greeting}");
        Debug.Log($"Cached farewell: {farewell}");
        
        // 清空缓存
        DataCacheManager.ClearCache();
    }
}
```

---

## 5. 注意事项

### 5.1 Unity iOS 构建设置

在 Unity 中进行 iOS 构建时，需要配置以下设置：

| 设置项 | 推荐值 | 说明 |
|--------|--------|------|
| **Enable Bitcode** | `No` 或 `Yes` | 根据需求设置，如需热更新建议关闭 |
| **Strip Engine Code** | `Disabled` | 关闭代码剥离，避免原生方法被移除 |
| **Architecture** | `ARM64` | 现代 iOS 设备要求 |
| **Target SDK** | `Device SDK` | 真机测试时使用 |

### 5.2 平台条件编译

始终使用平台条件编译来避免在编辑器中调用原生代码：

```csharp
#if UNITY_IOS && !UNITY_EDITOR
    // iOS 真机代码
    [DllImport("__Internal")]
    private static extern void NativeMethod();
#endif

public static void CallNative()
{
    #if UNITY_IOS && !UNITY_EDITOR
    NativeMethod();
    #else
    Debug.Log("[iOS Plugin] Running in Editor");
    #endif
}
```

### 5.3 真机测试要求

- **开发证书**：需要有效的 Apple 开发证书
- **Provisioning Profile**：配置正确的描述文件
- **设备 UDID**：测试设备需要添加到描述文件中
- **Xcode**：需要安装最新版本的 Xcode

### 5.4 内存管理

- Objective-C 返回的字符串由原生代码管理，C# 端使用 `Marshal.PtrToStringAnsi` 复制
- 避免在 C# 和原生代码之间传递大量数据
- 使用 `@autoreleasepool` 管理临时对象

---

## 6. 常见问题

### 6.1 编译错误处理

#### 错误：`Undefined symbol: _ABPrintStringConstants`

**原因**：链接器找不到符号定义

**解决方案**：
1. 确保 `.m` 文件在 `Assets/Plugins/iOS/` 目录下
2. 检查函数是否使用 `extern "C"` 或正确声明
3. 确认函数名拼写一致

#### 错误：`duplicate symbol`

**原因**：符号重复定义

**解决方案**：
1. 在头文件中使用 `extern` 声明
2. 在 `.m` 文件中实现函数
3. 避免在头文件中直接定义函数

### 6.2 链接错误处理

#### 错误：`library not found for -lABStringConstants`

**原因**：C# 的 `DllImport` 指定了错误的库名

**解决方案**：
```csharp
// 错误：指定了具体文件名
[DllImport("ABStringConstants")]

// 正确：使用 __Internal 链接所有 iOS 原生代码
[DllImport("__Internal")]
```

### 6.3 符号未找到错误

#### 错误：`EntryPointNotFoundException: ABPrintStringConstants`

**原因**：函数未正确导出

**解决方案**：
1. 确保函数使用 `extern` 声明为全局函数
2. 检查函数名大小写是否匹配
3. 确认代码在 iOS 构建时被包含

```objectivec
// 正确：全局函数
extern void ABPrintStringConstants() {
    // 实现
}

// 错误：类方法（不能直接通过 DllImport 调用）
@implementation MyClass
+ (void)printConstants { }
@end
```

### 6.4 字符串编码问题

#### 问题：中文乱码

**解决方案**：
```objectivec
// 使用 UTF8String 确保编码正确
extern const char* ABGetStringUTF8() {
    return [@"你好世界" UTF8String];
}
```

```csharp
// C# 端正确解码
[DllImport("__Internal")]
private static extern System.IntPtr ABGetStringUTF8();

string value = Marshal.PtrToStringUTF8(ABGetStringUTF8());
```

---

## 7. 附录

### 7.1 完整的 C# 包装类模板

```csharp
using System.Runtime.InteropServices;
using UnityEngine;

/// <summary>
/// iOS 原生插件包装类
/// </summary>
public class iOSNativePlugin
{
    #region Native Methods
    
    #if UNITY_IOS && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern void ABPrintStringConstants();
    
    [DllImport("__Internal")]
    private static extern System.IntPtr ABGetStringConstantUTF8(string key);
    
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_cacheString(string value, string key);
    
    [DllImport("__Internal")]
    private static extern System.IntPtr ABDataCacheManager_getCachedStringForKey(string key);
    
    [DllImport("__Internal")]
    private static extern void ABDataCacheManager_clearCache();
    #endif
    
    #endregion
    
    #region Public API
    
    public static void PrintStringConstants()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABPrintStringConstants();
        #else
        Debug.Log("[iOS Plugin] Editor mode - PrintStringConstants");
        #endif
    }
    
    public static string GetStringConstant(string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        System.IntPtr ptr = ABGetStringConstantUTF8(key);
        return Marshal.PtrToStringUTF8(ptr);
        #else
        return string.Empty;
        #endif
    }
    
    public static void CacheString(string value, string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_cacheString(value, key);
        #endif
    }
    
    public static string GetCachedString(string key)
    {
        #if UNITY_IOS && !UNITY_EDITOR
        System.IntPtr ptr = ABDataCacheManager_getCachedStringForKey(key);
        return Marshal.PtrToStringUTF8(ptr);
        #else
        return string.Empty;
        #endif
    }
    
    public static void ClearCache()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        ABDataCacheManager_clearCache();
        #endif
    }
    
    #endregion
}
```

### 7.2 参考链接

- [Unity iOS 原生插件文档](https://docs.unity3d.com/Manual/PluginsForIOS.html)
- [DllImport 属性](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.dllimportattribute)
- [Objective-C 与 C# 互操作](https://docs.unity3d.com/Manual/PlatformDependentCompilation.html)
