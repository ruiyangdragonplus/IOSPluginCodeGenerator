"""
代码生成中间表示 (IR / Spec)

唯一真相源：一个方法的签名（返回类型 + 参数）只在 MethodSpec 里定义一次，
头文件声明 与 实现定义 都从同一个 MethodSpec 渲染，从根本上杜绝"头实分叉"。

纯数据，无随机、无渲染逻辑。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set


# return_kind 取值（语言无关的返回语义）
RETURN_KINDS = {
    "void", "bool", "int", "float", "string", "object",
    "instancetype", "vector", "map", "pointer",
}

# 允许出现在函数体模板里的占位符前缀/名称（白名单）
# {arg0}..{argN} 形参名，{ret_default} 返回默认值，{self} self/this，{class_name} 类名
_PLACEHOLDER_RE_PARTS = ("ret_default", "self", "class_name")


@dataclass
class ParamSpec:
    """方法形参。"""
    name: str            # 形参名（C++ 统一 param0/param1...；OC 也用 param0...）
    type: str            # 语言相关最终类型串，如 "const std::string&" / "NSString *"
    role: str = "generic"  # 语义角色：key/value/message/callback/error/array/count/type/generic
    is_block_or_fn: bool = False


@dataclass
class PropertySpec:
    """属性 / 成员变量。"""
    name: str
    type: str
    attributes: str = "strong"   # OC: strong/assign/copy/weak
    access: str = "private"      # C++: private/public


@dataclass
class MethodSpec:
    """方法（唯一真相源）。"""
    name: str
    return_type: str
    return_kind: str
    language: str                       # "objc" | "cpp"
    params: List[ParamSpec] = field(default_factory=list)
    is_static: bool = False
    is_singleton: bool = False
    is_class_factory: bool = False
    template_id: str = ""
    body_template: List[str] = field(default_factory=list)
    provides_own_return: bool = False

    def __post_init__(self) -> None:
        if self.return_kind not in RETURN_KINDS:
            raise ValueError(
                f"非法 return_kind={self.return_kind!r}（方法 {self.name}）")
        if self.language not in ("objc", "cpp"):
            raise ValueError(f"非法 language={self.language!r}")
        # void 方法不应声称自带返回值之外的返回类型
        if self.return_kind == "void" and self.return_type not in ("void",):
            raise ValueError(
                f"return_kind=void 但 return_type={self.return_type!r}（方法 {self.name}）")


@dataclass
class ClassSpec:
    """一个类。"""
    name: str
    language: str
    parent_class: str = "NSObject"      # 仅 OC
    properties: List[PropertySpec] = field(default_factory=list)
    methods: List[MethodSpec] = field(default_factory=list)
    needs_singleton: bool = False
    extra_includes: Set[str] = field(default_factory=set)


# ---------------------------------------------------------------------------
# 返回类型 → return_kind 推导（穷举；漏配抛错而非静默降级）
# ---------------------------------------------------------------------------

def cpp_return_kind(return_type: str) -> str:
    rt = return_type.strip()
    if rt == "void":
        return "void"
    if rt == "bool":
        return "bool"
    if rt in ("int", "long", "short", "size_t", "NSInteger", "NSUInteger"):
        return "int"
    if rt in ("float", "double", "CGFloat"):
        return "float"
    if rt in ("std::string", "const std::string&"):
        return "string"
    if rt.startswith("std::vector"):
        return "vector"
    if rt.startswith("std::map") or rt.startswith("std::set"):
        return "map"
    if rt.startswith("std::unique_ptr") or rt.startswith("std::shared_ptr"):
        return "object"
    if rt.endswith("*") or rt.endswith("&"):
        return "pointer"
    # 默认按对象处理（如 ClassName&）
    return "object"


def objc_return_kind(return_type: str) -> str:
    rt = return_type.strip()
    if rt == "void":
        return "void"
    if rt == "BOOL":
        return "bool"
    if rt in ("NSInteger", "NSUInteger", "int", "long"):
        return "int"
    if rt in ("CGFloat", "float", "double"):
        return "float"
    if rt == "instancetype" or rt.startswith("instancetype"):
        return "instancetype"
    if "NSString" in rt:
        return "string"
    if rt.startswith("NSArray"):
        return "vector"
    if rt.startswith("NSDictionary"):
        return "map"
    # id / NSObject* / NSData* / NSError* 等
    return "object"


def return_kind_of(return_type: str, language: str) -> str:
    return cpp_return_kind(return_type) if language == "cpp" \
        else objc_return_kind(return_type)
