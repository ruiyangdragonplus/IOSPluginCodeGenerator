// MX11PluginWrapper.cs
// Unity C# 包装类 - 用于接入生成的 OC 和 C++ 插件代码
// 警告：此文件由工具自动生成，请勿手动修改

using System;
using System.Runtime.InteropServices;
using System.Text;

namespace MX11.Plugins
{
    #region OC 插件包装

    /// <summary>
    /// Objective-C 插件注册表包装类
    /// 提供对生成的 OC 插件代码的初始化和清理功能
    /// </summary>
    public static class MX11Plugin
    {
        private const string OCLibraryName = "__Internal";

        #region P/Invoke 声明

        /// <summary>
        /// 初始化所有 OC 插件（外部 C 函数）
        /// </summary>
        [DllImport(OCLibraryName, CallingConvention = CallingConvention.Cdecl)]
        private static extern void ABInitializeAllPlugins();

        /// <summary>
        /// 清理所有 OC 插件（外部 C 函数）
        /// </summary>
        [DllImport(OCLibraryName, CallingConvention = CallingConvention.Cdecl)]
        private static extern void ABCleanupAllPlugins();

        #endregion

        #region 公共方法

        /// <summary>
        /// 初始化所有 OC 插件
        /// 应在 Unity 应用启动时调用
        /// </summary>
        public static void InitializeAll()
        {
#if UNITY_IOS && !UNITY_EDITOR
            ABInitializeAllPlugins();
#else
            UnityEngine.Debug.Log("[MX11Plugin] InitializeAll called (non-iOS platform - no-op)");
#endif
        }

        /// <summary>
        /// 清理所有 OC 插件
        /// 应在 Unity 应用退出时调用
        /// </summary>
        public static void CleanupAll()
        {
#if UNITY_IOS && !UNITY_EDITOR
            ABCleanupAllPlugins();
#else
            UnityEngine.Debug.Log("[MX11Plugin] CleanupAll called (non-iOS platform - no-op)");
#endif
        }

        #endregion
    }

    #endregion

    #region C++ 插件包装

    /// <summary>
    /// C++ 插件注册表包装类
    /// 提供对生成的 C++ 插件代码的初始化和清理功能
    /// </summary>
    public static class MX11CppPlugin
    {
        private const string CppLibraryName = "__Internal";

        #region P/Invoke 声明

        /// <summary>
        /// 初始化所有 C++ 插件（外部 C 函数）
        /// </summary>
        [DllImport(CppLibraryName, CallingConvention = CallingConvention.Cdecl)]
        private static extern void ABInitializeAllPlugins();

        /// <summary>
        /// 清理所有 C++ 插件（外部 C 函数）
        /// </summary>
        [DllImport(CppLibraryName, CallingConvention = CallingConvention.Cdecl)]
        private static extern void ABCleanupAllPlugins();

        #endregion

        #region 公共方法

        /// <summary>
        /// 初始化所有 C++ 插件
        /// 应在 Unity 应用启动时调用
        /// </summary>
        public static void InitializeAll()
        {
#if UNITY_IOS && !UNITY_EDITOR
            ABInitializeAllPlugins();
#else
            UnityEngine.Debug.Log("[MX11CppPlugin] InitializeAll called (non-iOS platform - no-op)");
#endif
        }

        /// <summary>
        /// 清理所有 C++ 插件
        /// 应在 Unity 应用退出时调用
        /// </summary>
        public static void CleanupAll()
        {
#if UNITY_IOS && !UNITY_EDITOR
            ABCleanupAllPlugins();
#else
            UnityEngine.Debug.Log("[MX11CppPlugin] CleanupAll called (non-iOS platform - no-op)");
#endif
        }

        #endregion
    }

    #endregion

    #region OC String 常量访问

    /// <summary>
    /// Objective-C String 常量访问类
    /// 提供对生成的 OC String 常量的 P/Invoke 访问
    /// </summary>
    public static class MX11StringConstants
    {
        private const string StringLibraryName = "__Internal";

        #region P/Invoke 声明

        /// <summary>
        /// 获取 OC String 常量（返回 UTF-8 C 字符串）
        /// </summary>
        /// <param name="index">常量索引</param>
        /// <returns>UTF-8 编码的 C 字符串指针</returns>
        [DllImport(StringLibraryName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MX11GetStringConstant(int index);

        #endregion

        #region 缓存

        private static string[] _cachedConstants = null;
        private static readonly object _cacheLock = new object();

        #endregion

        #region 公共方法

        /// <summary>
        /// 获取指定索引的 String 常量
        /// </summary>
        /// <param name="index">常量索引 (0-9999)</param>
        /// <returns>String 常量值</returns>
        public static string GetConstant(int index)
        {
#if UNITY_IOS && !UNITY_EDITOR
            if (index < 0 || index >= 10000)
            {
                throw new ArgumentOutOfRangeException(nameof(index), "Index must be between 0 and 9999");
            }

            // 检查缓存
            if (_cachedConstants == null)
            {
                lock (_cacheLock)
                {
                    if (_cachedConstants == null)
                    {
                        _cachedConstants = new string[10000];
                    }
                }
            }

            // 返回缓存的值
            if (_cachedConstants[index] != null)
            {
                return _cachedConstants[index];
            }

            // 从原生代码获取
            IntPtr ptr = MX11GetStringConstant(index);
            if (ptr == IntPtr.Zero)
            {
                return string.Empty;
            }

            string value = Marshal.PtrToStringUTF8(ptr);
            _cachedConstants[index] = value ?? string.Empty;
            return _cachedConstants[index];
#else
            return $"[StringConstant_{index}]";
#endif
        }

        /// <summary>
        /// 获取所有 String 常量（批量访问，带缓存）
        /// </summary>
        /// <returns>包含所有常量的数组</returns>
        public static string[] GetAllConstants()
        {
#if UNITY_IOS && !UNITY_EDITOR
            if (_cachedConstants == null)
            {
                lock (_cacheLock)
                {
                    if (_cachedConstants == null)
                    {
                        _cachedConstants = new string[10000];
                        for (int i = 0; i < 10000; i++)
                        {
                            IntPtr ptr = MX11GetStringConstant(i);
                            if (ptr != IntPtr.Zero)
                            {
                                _cachedConstants[i] = Marshal.PtrToStringUTF8(ptr) ?? string.Empty;
                            }
                            else
                            {
                                _cachedConstants[i] = string.Empty;
                            }
                        }
                    }
                }
            }
            return _cachedConstants;
#else
            return new string[10000];
#endif
        }

        /// <summary>
        /// 清除缓存的常量
        /// </summary>
        public static void ClearCache()
        {
            lock (_cacheLock)
            {
                _cachedConstants = null;
            }
        }

        #endregion

        #region 索引器

        /// <summary>
        /// 通过索引访问 String 常量
        /// </summary>
        public static string this[int index] => GetConstant(index);

        #endregion
    }

    #endregion

    #region C++ String 常量访问

    /// <summary>
    /// C++ String 常量访问类
    /// 提供对生成的 C++ String 常量的 P/Invoke 访问
    /// </summary>
    public static class MX11CppStringConstants
    {
        private const string CppStringLibraryName = "__Internal";

        #region P/Invoke 声明

        /// <summary>
        /// 获取 C++ String 常量（返回 UTF-8 C 字符串）
        /// </summary>
        /// <param name="index">常量索引</param>
        /// <returns>UTF-8 编码的 C 字符串指针</returns>
        [DllImport(CppStringLibraryName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MX11CppGetStringConstant(int index);

        #endregion

        #region 缓存

        private static string[] _cachedConstants = null;
        private static readonly object _cacheLock = new object();

        #endregion

        #region 公共方法

        /// <summary>
        /// 获取指定索引的 String 常量
        /// </summary>
        /// <param name="index">常量索引 (0-9999)</param>
        /// <returns>String 常量值</returns>
        public static string GetConstant(int index)
        {
#if UNITY_IOS && !UNITY_EDITOR
            if (index < 0 || index >= 10000)
            {
                throw new ArgumentOutOfRangeException(nameof(index), "Index must be between 0 and 9999");
            }

            // 检查缓存
            if (_cachedConstants == null)
            {
                lock (_cacheLock)
                {
                    if (_cachedConstants == null)
                    {
                        _cachedConstants = new string[10000];
                    }
                }
            }

            // 返回缓存的值
            if (_cachedConstants[index] != null)
            {
                return _cachedConstants[index];
            }

            // 从原生代码获取
            IntPtr ptr = MX11CppGetStringConstant(index);
            if (ptr == IntPtr.Zero)
            {
                return string.Empty;
            }

            string value = Marshal.PtrToStringUTF8(ptr);
            _cachedConstants[index] = value ?? string.Empty;
            return _cachedConstants[index];
#else
            return $"[CppStringConstant_{index}]";
#endif
        }

        /// <summary>
        /// 获取所有 String 常量（批量访问，带缓存）
        /// </summary>
        /// <returns>包含所有常量的数组</returns>
        public static string[] GetAllConstants()
        {
#if UNITY_IOS && !UNITY_EDITOR
            if (_cachedConstants == null)
            {
                lock (_cacheLock)
                {
                    if (_cachedConstants == null)
                    {
                        _cachedConstants = new string[10000];
                        for (int i = 0; i < 10000; i++)
                        {
                            IntPtr ptr = MX11CppGetStringConstant(i);
                            if (ptr != IntPtr.Zero)
                            {
                                _cachedConstants[i] = Marshal.PtrToStringUTF8(ptr) ?? string.Empty;
                            }
                            else
                            {
                                _cachedConstants[i] = string.Empty;
                            }
                        }
                    }
                }
            }
            return _cachedConstants;
#else
            return new string[10000];
#endif
        }

        /// <summary>
        /// 清除缓存的常量
        /// </summary>
        public static void ClearCache()
        {
            lock (_cacheLock)
            {
                _cachedConstants = null;
            }
        }

        #endregion

        #region 索引器

        /// <summary>
        /// 通过索引访问 String 常量
        /// </summary>
        public static string this[int index] => GetConstant(index);

        #endregion
    }

    #endregion

    #region 统一插件管理器

    /// <summary>
    /// 统一插件管理器
    /// 提供对 OC 和 C++ 插件的统一初始化和清理
    /// </summary>
    public static class MX11PluginManager
    {
        private static bool _initialized = false;
        private static readonly object _initLock = new object();

        /// <summary>
        /// 获取插件是否已初始化
        /// </summary>
        public static bool IsInitialized => _initialized;

        /// <summary>
        /// 初始化所有插件（OC 和 C++）
        /// </summary>
        public static void Initialize()
        {
            lock (_initLock)
            {
                if (_initialized)
                {
                    return;
                }

#if UNITY_IOS && !UNITY_EDITOR
                UnityEngine.Debug.Log("[MX11PluginManager] Initializing all plugins...");
                
                // 初始化 OC 插件
                MX11Plugin.InitializeAll();
                
                // 初始化 C++ 插件
                MX11CppPlugin.InitializeAll();
                
                _initialized = true;
                
                UnityEngine.Debug.Log("[MX11PluginManager] All plugins initialized successfully");
#else
                UnityEngine.Debug.Log("[MX11PluginManager] Initialize called (non-iOS platform - no-op)");
                _initialized = true; // 标记为已初始化，避免重复调用
#endif
            }
        }

        /// <summary>
        /// 清理所有插件（OC 和 C++）
        /// </summary>
        public static void Cleanup()
        {
            lock (_initLock)
            {
                if (!_initialized)
                {
                    return;
                }

#if UNITY_IOS && !UNITY_EDITOR
                UnityEngine.Debug.Log("[MX11PluginManager] Cleaning up all plugins...");
                
                // 清理 C++ 插件（先清理后注册的）
                MX11CppPlugin.CleanupAll();
                
                // 清理 OC 插件
                MX11Plugin.CleanupAll();
                
                _initialized = false;
                
                // 清除常量缓存
                MX11StringConstants.ClearCache();
                MX11CppStringConstants.ClearCache();
                
                UnityEngine.Debug.Log("[MX11PluginManager] All plugins cleaned up successfully");
#else
                UnityEngine.Debug.Log("[MX11PluginManager] Cleanup called (non-iOS platform - no-op)");
                _initialized = false;
#endif
            }
        }

        /// <summary>
        /// 获取 OC String 常量
        /// </summary>
        public static string GetOCStringConstant(int index)
        {
            return MX11StringConstants.GetConstant(index);
        }

        /// <summary>
        /// 获取 C++ String 常量
        /// </summary>
        public static string GetCppStringConstant(int index)
        {
            return MX11CppStringConstants.GetConstant(index);
        }
    }

    #endregion

    #region Unity 生命周期管理器

    /// <summary>
    /// Unity 生命周期管理器组件
    /// 自动处理插件的初始化和清理
    /// </summary>
#if UNITY_5_3_OR_NEWER
    [UnityEngine.DisallowMultipleComponent]
    public class MX11PluginLifecycle : UnityEngine.MonoBehaviour
    {
        private static MX11PluginLifecycle _instance;

        /// <summary>
        /// 获取单例实例
        /// </summary>
        public static MX11PluginLifecycle Instance => _instance;

        /// <summary>
        /// 是否在 Awake 时自动初始化
        /// </summary>
        [UnityEngine.Tooltip("是否在应用启动时自动初始化插件")]
        public bool autoInitialize = true;

        private void Awake()
        {
            // 确保单例
            if (_instance == null)
            {
                _instance = this;
                UnityEngine.DontDestroyOnLoad(gameObject);
            }
            else
            {
                UnityEngine.Destroy(gameObject);
                return;
            }

            if (autoInitialize)
            {
                MX11PluginManager.Initialize();
            }
        }

        private void OnDestroy()
        {
            if (_instance == this)
            {
                MX11PluginManager.Cleanup();
                _instance = null;
            }
        }

        private void OnApplicationQuit()
        {
            MX11PluginManager.Cleanup();
        }

        private void OnApplicationPause(bool pause)
        {
            // 可选：在应用暂停/恢复时执行额外逻辑
            if (!pause)
            {
                // 应用恢复
                UnityEngine.Debug.Log("[MX11PluginLifecycle] Application resumed");
            }
        }
    }
#endif

    #endregion
}
