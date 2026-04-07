using System;
using System.Runtime.InteropServices;

/// <summary>
/// ABPlugin 包装类 - 用于 Unity iOS 项目中调用原生插件
/// 
/// 使用方法:
/// 1. 将此文件添加到 Unity 项目的 Assets/Plugins 目录
/// 2. 在需要初始化的地方调用 ABPluginWrapper.InitializeAll()
/// 3. 在清理时调用 ABPluginWrapper.CleanupAll()
/// 
/// 注意：此包装类仅在 iOS 真机上生效，编辑器模式下不会执行任何操作
/// </summary>
public class ABPluginWrapper
{
    // 声明外部原生函数
    [DllImport("__Internal")]
    private static extern void ABInitializeAllPlugins();
    
    [DllImport("__Internal")]
    private static extern void ABCleanupAllPlugins();
    
    /// <summary>
    /// 初始化所有插件（调用所有生成的类）
    /// 在应用启动时调用此方法
    /// </summary>
    public static void InitializeAll()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        try
        {
            ABInitializeAllPlugins();
            UnityEngine.Debug.Log("[ABPlugin] All plugins initialized.");
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError($"[ABPlugin] Failed to initialize: {e.Message}");
        }
        #endif
    }
    
    /// <summary>
    /// 清理所有插件
    /// 在应用退出前调用此方法
    /// </summary>
    public static void CleanupAll()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        try
        {
            ABCleanupAllPlugins();
            UnityEngine.Debug.Log("[ABPlugin] All plugins cleaned up.");
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError($"[ABPlugin] Failed to cleanup: {e.Message}");
        }
        #endif
    }
    
    /// <summary>
    /// 检查插件是否已初始化（仅用于调试）
    /// </summary>
    /// <returns>如果插件已初始化返回 true</returns>
    public static bool IsInitialized()
    {
        #if UNITY_IOS && !UNITY_EDITOR
        // 注意：需要在原生端添加查询函数
        return true;
        #else
        return false;
        #endif
    }
}

/// <summary>
/// 自动初始化器 - 在场景加载时自动初始化插件
/// 将此脚本挂载到场景中的 GameObject 上
/// </summary>
public class ABPluginAutoInitializer : MonoBehaviour
{
    void Awake()
    {
        // 确保在场景加载时初始化
        ABPluginWrapper.InitializeAll();
        
        // 注册应用程序退出事件
        Application.quitting += OnApplicationQuit;
    }
    
    void OnApplicationQuit()
    {
        // 清理插件
        ABPluginWrapper.CleanupAll();
    }
    
    void OnDestroy()
    {
        // 注销事件
        Application.quitting -= OnApplicationQuit;
    }
}
