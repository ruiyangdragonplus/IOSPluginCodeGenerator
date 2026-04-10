# Unity iOS 插件接入指南

本文档说明如何将生成的 Objective-C 和 C++ 代码集成到 Unity 项目中，并在 iOS 平台上使用。

## 目录

- [概述](#概述)
- [文件结构](#文件结构)
- [编译静态库](#编译静态库)
- [Unity 项目配置](#unity 项目配置)
- [C# 包装类使用](#c-包装类使用)
- [示例代码](#示例代码)
- [故障排除](#故障排除)

---

## 概述

本插件系统包含以下组件：

1. **Objective-C 插件代码** - 生成的 OC 类和方法
2. **C++ 插件代码** - 生成的 C++ 类和方法
3. **String 常量** - OC 和 C++ 的字符串常量表
4. **注册表** - 插件初始化和清理的统一入口
5. **C# 包装类** - Unity 中使用的 P/Invoke 包装

---

## 文件结构

### 生成的代码目录

```
production/
├── oc_code/                    # Objective-C 源代码
│   ├── ABPluginRegistry.h      # OC 插件注册表头文件
│   ├── ABPluginRegistry.m      # OC 插件注册表实现
│   ├── MX11*.h                 # 生成的 OC 类头文件
│   └── MX11*.m                 # 生成的 OC 类实现
├── cpp_code/                   # C++ 源代码
│   ├── ABPluginRegistry.h      # C++ 插件注册表头文件
│   ├── ABPluginRegistry.cpp    # C++ 插件注册表实现
│   ├── MX11*.hpp               # 生成的 C++ 类头文件
│   └── MX11*.cpp               # 生成的 C++ 类实现
└── oc_string/                  # String 常量
    └── MX11StringConstants.m   # OC String 常量定义
```

### Unity 项目目录

```
YourUnityProject/
├── Assets/
│   ├── Plugins/
│   │   └── iOS/
│   │       ├── libMX11OCPlugin.a       # OC 静态库
│   │       ├── libMX11CppPlugin.a      # C++ 静态库
│   │       ├── libMX11StringConstants.a # String 常量库
│   │       └── MX11PluginWrapper.cs    # C# 包装类
│   └── Scripts/
│       └── MX11/
│           └── MX11PluginWrapper.cs    # 或者放在这里
```

---

## 编译静态库

### 前置要求

- macOS 系统
- Xcode 14.0 或更高版本
- Xcode Command Line Tools

### 步骤 1: 创建 Xcode 项目

创建一个新的 Xcode Framework 项目或使用现有的项目。

### 步骤 2: 添加源代码文件

将生成的源代码文件添加到 Xcode 项目中：

```bash
# 复制 OC 代码
cp production/oc_code/*.h /path/to/XcodeProject/
cp production/oc_code/*.m /path/to/XcodeProject/

# 复制 C++ 代码
cp production/cpp_code/*.h /path/to/XcodeProject/
cp production/cpp_code/*.cpp /path/to/XcodeProject/

# 复制 String 常量
cp production/oc_string/MX11StringConstants.m /path/to/XcodeProject/
```

### 步骤 3: 配置编译设置

在 Xcode 中配置以下设置：

1. **Build Settings → Architectures**
   - 设置为 `Standard architectures (armv7, arm64)`

2. **Build Settings → Build Active Architecture Only**
   - Debug: `No`
   - Release: `No`

3. **Build Settings → Objective-C Bridging Header** (如果需要 Swift)
   - 添加桥接头文件路径

### 步骤 4: 编译静态库

使用以下命令编译静态库：

```bash
# 编译 OC 静态库
xcodebuild -project MX11Plugin.xcodeproj \
    -scheme MX11OCPlugin \
    -configuration Release \
    -sdk iphoneos \
    archive

# 编译 C++ 静态库
xcodebuild -project MX11Plugin.xcodeproj \
    -scheme MX11CppPlugin \
    -configuration Release \
    -sdk iphoneos \
    archive
```

### 步骤 5: 提取静态库文件

编译完成后，从归档中提取 `.a` 文件：

```bash
# 找到归档目录
cd ~/Library/Developer/Xcode/DerivedData/

# 复制静态库到 Unity 项目
cp -R */Build/Products/Release-iphoneos/*.a /path/to/UnityProject/Assets/Plugins/iOS/
```

### 替代方案：使用命令行编译

如果不想使用 Xcode GUI，可以使用命令行直接编译：

```bash
# 编译 OC 静态库
clang -arch arm64 -arch armv7 -isysroot $(xcrun --sdk iphoneos --show-sdk-path) \
    -c production/oc_code/*.m -o oc_objects.o
libtool -static -o libMX11OCPlugin.a oc_objects.o -framework Foundation

# 编译 C++ 静态库
clang++ -arch arm64 -arch armv7 -isysroot $(xcrun --sdk iphoneos --show-sdk-path) \
    -std=c++17 -c production/cpp_code/*.cpp -o cpp_objects.o
libtool -static -o libMX11CppPlugin.a cpp_objects.o

# 移动库文件到 Unity
mv libMX11*.a /path/to/UnityProject/Assets/Plugins/iOS/
```

---

## Unity 项目配置

### 1. 导入 C# 包装类

将 [`MX11PluginWrapper.cs`](MX11PluginWrapper.cs) 文件复制到 Unity 项目的 `Assets/Scripts/` 目录。

### 2. 配置 iOS 插件设置

在 Unity 中，确保 iOS 插件设置正确：

1. 选择 `Assets/Plugins/iOS/` 目录下的 `.a` 文件
2. 在 Inspector 中确认：
   - **Select platforms for plugin**: 勾选 `iOS`
   - **CPU**: 勾选 `ARM64` 和 `ARMv7`
   - **Usage**: 设置为 `Any Language`

### 3. 配置 Build Settings

1. 打开 `File → Build Settings`
2. 选择 `iOS` 平台
3. 点击 `Switch Platform`
4. 点击 `Player Settings`
5. 在 `Other Settings` 中：
   - **Scripting Backend**: 设置为 `IL2CPP`
   - **Target SDK**: 设置为 `Device SDK`
   - **Architecture**: 设置为 `ARM64`

### 4. 添加初始化代码

创建一个初始化脚本：

```csharp
using UnityEngine;
using MX11.Plugins;

public class PluginInitializer : MonoBehaviour
{
    private void Awake()
    {
        // 初始化所有插件
        MX11PluginManager.Initialize();
        
        // 或者分别初始化
        // MX11Plugin.InitializeAll();
        // MX11CppPlugin.InitializeAll();
        
        DontDestroyOnLoad(gameObject);
    }

    private void OnApplicationQuit()
    {
        // 清理所有插件
        MX11PluginManager.Cleanup();
    }

    private void OnApplicationPause(bool pause)
    {
        if (!pause)
        {
            // 应用恢复时重新初始化（如果需要）
            if (!MX11PluginManager.IsInitialized)
            {
                MX11PluginManager.Initialize();
            }
        }
    }
}
```

---

## C# 包装类使用

### 插件初始化

```csharp
using MX11.Plugins;

// 方法 1: 使用统一管理器（推荐）
MX11PluginManager.Initialize();

// 方法 2: 分别初始化
MX11Plugin.InitializeAll();      // OC 插件
MX11CppPlugin.InitializeAll();   // C++ 插件
```

### 插件清理

```csharp
// 方法 1: 使用统一管理器（推荐）
MX11PluginManager.Cleanup();

// 方法 2: 分别清理
MX11CppPlugin.CleanupAll();      // C++ 插件（先清理）
MX11Plugin.CleanupAll();         // OC 插件
```

### 访问 String 常量

```csharp
using MX11.Plugins;

// 访问 OC String 常量
string ocString = MX11StringConstants.GetConstant(0);
string ocString2 = MX11StringConstants[100];  // 使用索引器

// 访问 C++ String 常量
string cppString = MX11CppStringConstants.GetConstant(0);
string cppString2 = MX11CppStringConstants[100];  // 使用索引器

// 批量获取所有常量（带缓存）
string[] allOcConstants = MX11StringConstants.GetAllConstants();
string[] allCppConstants = MX11CppStringConstants.GetAllConstants();

// 通过管理器访问
string constant = MX11PluginManager.GetOCStringConstant(42);
string cppConstant = MX11PluginManager.GetCppStringConstant(42);
```

### 使用生命周期组件

```csharp
using UnityEngine;
using MX11.Plugins;

public class SetupPluginLifecycle : MonoBehaviour
{
    private void Start()
    {
        // 创建生命周期管理器
        var lifecycleObj = new GameObject("MX11PluginLifecycle");
        var lifecycle = lifecycleObj.AddComponent<MX11PluginLifecycle>();
        lifecycle.autoInitialize = true;  // 自动初始化
    }
}
```

---

## 示例代码

### 完整示例：插件管理器

```csharp
using UnityEngine;
using MX11.Plugins;

/// <summary>
/// 完整的插件使用示例
/// </summary>
public class MX11PluginExample : MonoBehaviour
{
    [Header("插件设置")]
    [Tooltip("是否在启动时自动初始化")]
    public bool autoInitialize = true;
    
    [Header("String 常量")]
    [Tooltip("要显示的常量索引")]
    public int constantIndex = 0;

    private void Start()
    {
        if (autoInitialize)
        {
            InitializePlugins();
        }
    }

    /// <summary>
    /// 初始化插件
    /// </summary>
    public void InitializePlugins()
    {
        Debug.Log("正在初始化 MX11 插件...");
        
        try
        {
            MX11PluginManager.Initialize();
            Debug.Log("MX11 插件初始化成功！");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"MX11 插件初始化失败：{e.Message}");
        }
    }

    /// <summary>
    /// 获取并显示 String 常量
    /// </summary>
    public void DisplayStringConstant()
    {
        if (!MX11PluginManager.IsInitialized)
        {
            Debug.LogWarning("插件未初始化，请先调用 InitializePlugins()");
            return;
        }

        string ocConstant = MX11StringConstants.GetConstant(constantIndex);
        string cppConstant = MX11CppStringConstants.GetConstant(constantIndex);

        Debug.Log($"OC String 常量 [{constantIndex}]: {ocConstant}");
        Debug.Log($"C++ String 常量 [{constantIndex}]: {cppConstant}");
    }

    /// <summary>
    /// 批量测试 String 常量访问
    /// </summary>
    public void TestStringConstants()
    {
        if (!MX11PluginManager.IsInitialized)
        {
            Debug.LogWarning("插件未初始化");
            return;
        }

        Debug.Log("开始测试 String 常量访问...");
        
        // 测试前 10 个常量
        for (int i = 0; i < 10; i++)
        {
            string oc = MX11StringConstants[i];
            string cpp = MX11CppStringConstants[i];
            Debug.Log($"[{i}] OC: {oc} | C++: {cpp}");
        }

        Debug.Log("String 常量测试完成");
    }

    private void OnApplicationQuit()
    {
        Debug.Log("正在清理 MX11 插件...");
        MX11PluginManager.Cleanup();
        Debug.Log("MX11 插件清理完成");
    }

    private void OnGUI()
    {
        GUILayout.BeginArea(new Rect(10, 10, 300, 500));
        
        GUILayout.Label("MX11 插件示例");
        GUILayout.Space(10);

        GUILayout.Label($"插件状态：{(MX11PluginManager.IsInitialized ? "已初始化" : "未初始化")}");
        
        GUILayout.Space(10);

        if (GUILayout.Button("初始化插件"))
        {
            InitializePlugins();
        }

        if (GUILayout.Button("显示 String 常量"))
        {
            DisplayStringConstant();
        }

        if (GUILayout.Button("测试 String 常量"))
        {
            TestStringConstants();
        }

        GUILayout.Space(10);
        
        GUILayout.Label("常量索引:");
        string indexStr = GUILayout.TextField(constantIndex.ToString());
        if (int.TryParse(indexStr, out int idx) && idx >= 0 && idx < 10000)
        {
            constantIndex = idx;
        }

        if (GUILayout.Button("清理插件"))
        {
            MX11PluginManager.Cleanup();
        }

        GUILayout.EndArea();
    }
}
```

### 示例：使用生命周期组件

```csharp
using UnityEngine;
using MX11.Plugins;

/// <summary>
/// 演示如何使用生命周期组件
/// </summary>
public class LifecycleExample : MonoBehaviour
{
    private void Start()
    {
        // 创建带有生命周期管理的游戏对象
        var pluginManager = new GameObject("PluginManager");
        var lifecycle = pluginManager.AddComponent<MX11PluginLifecycle>();
        lifecycle.autoInitialize = true;

        // 等待一帧后访问常量
        StartCoroutine(AccessConstantsAfterInit());
    }

    private System.Collections.IEnumerator AccessConstantsAfterInit()
    {
        yield return new WaitForEndOfFrame();

        // 现在可以安全地访问常量
        string constant = MX11StringConstants[0];
        Debug.Log($"String 常量：{constant}");
    }
}
```

### 示例：异步加载场景时使用

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;
using MX11.Plugins;

/// <summary>
/// 在异步加载场景时使用插件
/// </summary>
public class AsyncSceneLoader : MonoBehaviour
{
    public string sceneName;

    private void Start()
    {
        // 确保插件已初始化
        MX11PluginManager.Initialize();
    }

    public void LoadScene()
    {
        StartCoroutine(LoadSceneAsync());
    }

    private System.Collections.IEnumerator LoadSceneAsync()
    {
        Debug.Log($"开始加载场景：{sceneName}");
        
        var operation = SceneManager.LoadSceneAsync(sceneName);
        
        while (!operation.isDone)
        {
            // 可以在这里显示加载进度
            Debug.Log($"加载进度：{operation.progress * 100:F1}%");
            yield return null;
        }

        Debug.Log("场景加载完成");
    }

    private void OnDestroy()
    {
        // 可选：在场景卸载时清理
        // MX11PluginManager.Cleanup();
    }
}
```

---

## 故障排除

### 常见问题

#### 1. 编译错误：找不到库文件

**问题**: Unity 报告找不到 `.a` 库文件

**解决方案**:
- 确保库文件位于 `Assets/Plugins/iOS/` 目录
- 检查文件扩展名是否正确（`.a`）
- 在 Finder 中右键文件 → Get Info，确认文件类型

#### 2. 链接错误：未定义的符号

**问题**: 编译时报告 `undefined symbol: ABInitializeAllPlugins`

**解决方案**:
- 确保所有必要的 `.a` 文件都已添加到项目
- 检查库文件是否包含正确的架构（arm64, armv7）
- 使用 `lipo -info libMX11OCPlugin.a` 检查架构

#### 3. 运行时错误：DllNotFoundException

**问题**: 运行时报告 `DllNotFoundException: __Internal`

**解决方案**:
- 确保在 iOS 设备上运行（模拟器可能不支持）
- 检查 P/Invoke 声明中的库名是否正确
- 确认代码在 `#if UNITY_IOS && !UNITY_EDITOR` 条件下执行

#### 4. String 常量返回空值

**问题**: `GetConstant()` 返回空字符串

**解决方案**:
- 确保插件已初始化
- 检查索引是否在有效范围内（0-9999）
- 确认 String 常量库已正确编译和链接

### 调试技巧

#### 检查库文件

```bash
# 检查库文件包含的架构
lipo -info libMX11OCPlugin.a

# 检查库文件中的符号
nm libMX11OCPlugin.a | grep ABInitializeAllPlugins

# 检查 OC String 常量符号
nm libMX11StringConstants.a | grep MX11StringConstant
```

#### Unity 日志

在 Unity 中启用详细日志：

```csharp
// 在初始化前添加
UnityEngine.Debug.unityLogger.logEnabled = true;
```

#### Xcode 控制台

在 Xcode 中运行 Unity 导出的项目时，查看控制台日志：

```
[MX11Plugin] InitializeAll called
[MX11PluginManager] Initializing all plugins...
[MX11PluginManager] All plugins initialized successfully
```

### 联系支持

如果遇到问题，请提供以下信息：

1. Unity 版本
2. Xcode 版本
3. iOS 版本
4. 完整的错误日志
5. 复现步骤

---

## 附录

### P/Invoke 签名参考

```csharp
// OC 插件初始化
[DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
private static extern void ABInitializeAllPlugins();

// OC 插件清理
[DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
private static extern void ABCleanupAllPlugins();

// 获取 String 常量
[DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
private static extern IntPtr MX11GetStringConstant(int index);
```

### 生成的类列表

以下是生成的部分类名（完整列表请参考生成的代码目录）：

**Objective-C 类**:
- MX11ActiveCalendarParameter
- MX11ActiveContextAirport
- MX11ActiveDecoratorVenus
- ... (更多类)

**C++ 类**:
- MX11AuthenticatedTreeArea
- MX11AuthenticatedVectorColumn
- MX11AuthenticatedVisitorConstant
- ... (更多类)

### 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2024-01-01 | 初始版本 |
| 1.0.1 | 2024-01-15 | 添加 String 常量访问 |
| 1.0.2 | 2024-02-01 | 添加生命周期组件 |
