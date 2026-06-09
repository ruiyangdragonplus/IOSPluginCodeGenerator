#!/usr/bin/env python3
"""
产物校验门禁

两层校验：
1. 结构校验（纯 Python，无外部依赖，跨平台）—— 主力门禁
   - 头文件方法声明 与 实现签名 是否逐字一致（根治"头实分叉"）
   - 函数体是否引用了未声明的标识符（根治"未声明变量"）
   - 单个方法体内是否存在不可达的重复 return（根治"双 return"）
   - return 语句是否与声明返回类型自洽（根治"返回类型冲突"）
2. clang/clang++ -fsyntax-only 编译校验（可选）—— clang 缺失时自动降级跳过
   仅在 CI / macOS 上强制；Windows 开发机通常无 clang。

用法：
    python -m tools.syntax_check <dir_or_file> [...]      # 校验已有产物
    python tools/syntax_check.py output_cpp_test          # 同上

退出码：0=全部通过，1=发现问题。
"""

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class Signature:
    """一个方法的规范化签名（语言无关）。"""
    name: str            # 方法名（C++）或完整选择器（OC，含参数标签）
    return_part: str     # 规范化返回类型
    params: str          # 规范化参数串
    raw: str             # 原始行（用于报错展示）


@dataclass
class Issue:
    file: str
    kind: str
    detail: str


@dataclass
class Report:
    issues: List[Issue] = field(default_factory=list)
    files_checked: int = 0
    clang_ran: bool = False

    def add(self, file: str, kind: str, detail: str) -> None:
        self.issues.append(Issue(file, kind, detail))

    @property
    def ok(self) -> bool:
        return not self.issues


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    """折叠空白，便于逐字比对。"""
    return re.sub(r"\s+", " ", s).strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# 体内常见硬编码标识符（占位符化前的"问题变量"）。
# 出现在函数体却未在参数/已知成员中声明 → 编译必报未声明标识符。
_SUSPECT_IDENTS = {
    "key", "value", "block", "completion", "callback", "items",
    "count", "maxCount", "message", "array", "error",
}

# 生成器在类里硬塞的支撑成员/局部约定，视为"已声明"，不算问题。
_KNOWN_MEMBERS_CPP = {
    "cache_", "name_", "initialized_", "count_", "maxCount_",
    "ptr_", "obj_", "index_", "size_", "currentValue_", "instance", "this",
}
_KNOWN_MEMBERS_OC = {
    "cache", "delegate", "self", "error", "success", "result",
    "cached", "cacheKey", "fetched",
}


def _ident_declared_in_body(ident: str, body: str) -> bool:
    """该标识符是否在 body 内被本地声明（粗判：出现在赋值/声明左侧）。"""
    # 形如 `Type ident =` 或 `Type *ident =` 或 `auto ident =`
    return bool(re.search(rf"\b\w[\w:<>*&\s]*\b{re.escape(ident)}\s*=", body)) or \
        bool(re.search(rf"\bfor\s*\(\s*\w[\w\s*]*\b{re.escape(ident)}\b", body))


# ---------------------------------------------------------------------------
# C++ 解析
# ---------------------------------------------------------------------------

def _cpp_header_decls(text: str, class_name: str) -> Dict[str, Signature]:
    """从 .h 提取方法声明（跳过构造/析构）。"""
    out: Dict[str, Signature] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.endswith(";") or "(" not in line:
            continue
        m = re.match(r"^(.*?)\b([A-Za-z_]\w*)\s*\((.*)\)\s*;$", line)
        if not m:
            continue
        ret, name, params = m.group(1), m.group(2), m.group(3)
        if name == class_name or ret.strip().endswith("~"):  # 构造/析构
            continue
        ret_norm = _norm(ret.replace("static", "").replace("virtual", ""))
        out[name] = Signature(name, ret_norm, _norm(params), line)
    return out


def _cpp_impl_defs(text: str, class_name: str) -> Dict[str, Signature]:
    """从 .cpp 提取方法定义签名（跳过构造/析构）。"""
    out: Dict[str, Signature] = {}
    pat = re.compile(
        rf"^(.*?)\b{re.escape(class_name)}::([A-Za-z_]\w*)\s*\((.*)\)\s*\{{",
    )
    for raw in text.splitlines():
        line = raw.strip()
        m = pat.match(line)
        if not m:
            continue
        ret, name, params = m.group(1), m.group(2), m.group(3)
        if name == class_name or name.startswith("~"):
            continue
        ret_norm = _norm(ret.replace("static", "").replace("virtual", ""))
        out[name] = Signature(name, ret_norm, _norm(params), line)
    return out


def _split_cpp_methods(text: str, class_name: str) -> List[Tuple[Signature, str]]:
    """切出每个方法定义的函数体（用于体级校验）。返回 (签名, body)。"""
    results: List[Tuple[Signature, str]] = []
    pat = re.compile(
        rf"^(.*?)\b{re.escape(class_name)}::([A-Za-z_]\w*)\s*\((.*)\)\s*\{{\s*$",
        re.MULTILINE,
    )
    matches = list(pat.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(2)
        if name == class_name or name.startswith("~"):
            continue
        start = m.end()
        # 用花括号配平找函数体结束
        depth = 1
        j = start
        while j < len(text) and depth > 0:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[start:j - 1]
        sig = Signature(name, _norm(m.group(1)), _norm(m.group(3)), m.group(0).strip())
        results.append((sig, body))
    return results


# ---------------------------------------------------------------------------
# OC 解析
# ---------------------------------------------------------------------------

_OC_METHOD_RE = re.compile(r"^\s*([+-])\s*\(([^)]*)\)\s*(.*?)\s*([;{])\s*$")


def _oc_selector(decl_body: str) -> str:
    """从 OC 方法体（去掉 +/- 和返回类型后）提取选择器关键字串作为 key。"""
    # 取所有 label:（带冒号的关键字），无参方法取整串
    labels = re.findall(r"(\w+):", decl_body)
    if labels:
        return ":".join(labels) + ":"
    return decl_body.strip()


def _oc_methods(text: str, want: str) -> Dict[str, Signature]:
    """提取 OC 方法（want='decl' 取以;结尾的声明，want='impl' 取以{结尾的定义）。"""
    out: Dict[str, Signature] = {}
    terminator = ";" if want == "decl" else "{"
    for raw in text.splitlines():
        m = _OC_METHOD_RE.match(raw)
        if not m or m.group(4) != terminator:
            continue
        sign, ret, sel_body = m.group(1), m.group(2), m.group(3)
        key = sign + _oc_selector(sel_body)
        full = f"{sign} ({_norm(ret)}){_norm(sel_body)}"
        out[key] = Signature(key, _norm(ret), _norm(sel_body), full)
    return out


def _oc_method_bodies(text: str) -> List[Tuple[str, str]]:
    """切出 OC 实现方法体。返回 (签名行, body)。"""
    results: List[Tuple[str, str]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = _OC_METHOD_RE.match(lines[i])
        if m and m.group(4) == "{":
            sig_line = lines[i].strip()
            depth = lines[i].count("{") - lines[i].count("}")
            body_lines = []
            i += 1
            while i < len(lines) and depth > 0:
                depth += lines[i].count("{") - lines[i].count("}")
                if depth > 0:
                    body_lines.append(lines[i])
                i += 1
            results.append((sig_line, "\n".join(body_lines)))
        else:
            i += 1
    return results


# ---------------------------------------------------------------------------
# 体级校验（语言无关启发式）
# ---------------------------------------------------------------------------

def _strip_noncode(text: str) -> str:
    """剥离注释与字符串/字符字面量，避免在其中误匹配标识符。"""
    out = []
    for line in text.splitlines():
        # 去掉行注释
        line = re.sub(r"//.*$", "", line)
        # 去掉字符串/字符字面量内容（保留引号外的代码）
        line = re.sub(r'@?"(\\.|[^"\\])*"', '""', line)
        line = re.sub(r"'(\\.|[^'\\])*'", "''", line)
        out.append(line)
    # 去掉块注释
    joined = "\n".join(out)
    joined = re.sub(r"/\*.*?\*/", "", joined, flags=re.DOTALL)
    return joined


# 模板中调用但从未声明的"辅助方法"——出现即编译错误（未声明选择器/成员函数）
_UNDECLARED_HELPERS = {
    "fetchValue", "fetchValueForKey", "processItem", "processObject",
    "processResult", "transformItem", "writeLog", "setup",
}


def _check_body(file: str, sig: str, body: str, params: str,
                known: set, report: Report,
                return_void: Optional[bool] = None) -> None:
    # 参数串里所有标识符 token 都视为已声明（含 param0、key、block 等真实名）
    declared = set(re.findall(r"[A-Za-z_]\w*", params)) | known
    # 仅在"代码"上扫描可疑标识符（剔除注释/字符串字面量）
    code = _strip_noncode(body)

    # 0) 调用未声明的辅助方法
    for helper in sorted(_UNDECLARED_HELPERS):
        if re.search(rf"\b{helper}\b", code):
            report.add(file, "undeclared-call",
                       f"方法 [{sig}] 调用了未声明的辅助方法 '{helper}'")

    # 0b) 返回语句与声明返回类型一致性
    if return_void is not None:
        ret_vals = re.findall(r"\breturn\b([^;]*);", code)
        if return_void:
            for rv in ret_vals:
                if rv.strip():  # void 方法却 return 了值
                    report.add(file, "void-returns-value",
                               f"方法 [{sig}] 声明 void 却 return '{rv.strip()}'")
                    break
        else:
            if not any(rv.strip() for rv in ret_vals):
                report.add(file, "missing-return",
                           f"方法 [{sig}] 声明非 void 却无有效 return")

    # 1) 未声明的可疑标识符
    for ident in sorted(_SUSPECT_IDENTS):
        if ident in declared:
            continue
        # 负向后顾：排除成员访问 obj.count / obj->count（不是独立变量）
        if re.search(rf"(?<![\w.>]){ident}\b", code) and not _ident_declared_in_body(ident, code):
            report.add(file, "undeclared-ident",
                       f"方法 [{sig}] 体内引用未声明标识符 '{ident}'")

    # 2) 同层级双 return（粗判：两条独立 return 语句之间无控制流）
    return_lines = [ln.strip() for ln in body.splitlines()
                    if re.match(r"^\s*return\b", ln)]
    # 末尾连续两条裸 return 视为不可达
    tail = [ln for ln in body.splitlines() if ln.strip().startswith("return ")
            or ln.strip() == "return;"]
    if len(tail) >= 2 and _norm(tail[-2]).rstrip(";") and _norm(tail[-1]):
        # 仅当最后两条 return 缩进相同（同层）时才判定
        last_two = [ln for ln in body.splitlines()
                    if ln.strip().startswith("return")][-2:]
        if len(last_two) == 2 and \
                (len(last_two[0]) - len(last_two[0].lstrip())) == \
                (len(last_two[1]) - len(last_two[1].lstrip())):
            report.add(file, "double-return",
                       f"方法 [{sig}] 末尾存在不可达的重复 return")


# ---------------------------------------------------------------------------
# 单类校验
# ---------------------------------------------------------------------------

def check_cpp_class(header: Path, impl: Path, report: Report) -> None:
    class_name = header.stem
    htext, itext = _read(header), _read(impl)
    decls = _cpp_header_decls(htext, class_name)
    defs = _cpp_impl_defs(itext, class_name)

    for name, dsig in defs.items():
        hsig = decls.get(name)
        if hsig is None:
            report.add(str(impl), "missing-decl",
                       f"实现 {name}(...) 在头文件中无声明")
            continue
        if hsig.return_part != dsig.return_part or hsig.params != dsig.params:
            report.add(str(impl), "sig-mismatch",
                       f"{name}: 头[{hsig.return_part} ({hsig.params})] "
                       f"≠ 实现[{dsig.return_part} ({dsig.params})]")

    for sig, body in _split_cpp_methods(itext, class_name):
        is_void = sig.return_part.strip() == "void"
        _check_body(str(impl), sig.name, body, sig.params, _KNOWN_MEMBERS_CPP,
                    report, return_void=is_void)


def check_oc_class(header: Path, impl: Path, report: Report) -> None:
    htext, itext = _read(header), _read(impl)
    decls = _oc_methods(htext, "decl")
    defs = _oc_methods(itext, "impl")

    for key, dsig in defs.items():
        hsig = decls.get(key)
        if hsig is None:
            report.add(str(impl), "missing-decl",
                       f"实现 [{dsig.raw}] 在头文件中无匹配声明")
            continue
        if hsig.return_part != dsig.return_part or hsig.params != dsig.params:
            report.add(str(impl), "sig-mismatch",
                       f"{key}: 头[{hsig.raw}] ≠ 实现[{dsig.raw}]")

    for sig_line, body in _oc_method_bodies(itext):
        # OC 参数名 = 紧跟每个 ')' 之后的标识符（兼容 block 类型 (void(^)(...))name）
        params = " ".join(re.findall(r"\)\s*(\w+)", sig_line))
        rm = re.match(r"^\s*[+-]\s*\(([^)]*)\)", sig_line)
        is_void = bool(rm) and rm.group(1).strip() == "void"
        _check_body(str(impl), sig_line, body, params, _KNOWN_MEMBERS_OC,
                    report, return_void=is_void)


# ---------------------------------------------------------------------------
# clang 可选编译校验
# ---------------------------------------------------------------------------

def _clang_available() -> Tuple[Optional[str], Optional[str]]:
    return shutil.which("clang"), shutil.which("clang++")


def run_clang(files: List[Path], report: Report) -> None:
    clang, clangpp = _clang_available()
    if not clang and not clangpp:
        print("  [clang] 未检测到 clang/clang++，跳过编译校验（CI/macOS 上强制）")
        return
    report.clang_ran = True
    sdk = None
    xcrun = shutil.which("xcrun")
    if xcrun:
        try:
            sdk = subprocess.check_output(
                [xcrun, "--show-sdk-path"], text=True).strip()
        except Exception:
            sdk = None
    for f in files:
        out_dir = str(f.parent)
        if f.suffix == ".cpp" and clangpp:
            cmd = [clangpp, "-std=c++14", "-fsyntax-only",
                   "-Wunreachable-code", "-Werror=return-type",
                   f"-I{out_dir}", str(f)]
        elif f.suffix == ".m" and clang:
            cmd = [clang, "-fsyntax-only", "-x", "objective-c", "-fobjc-arc",
                   "-Wunreachable-code", "-Werror=return-type",
                   f"-I{out_dir}", str(f)]
            if sdk:
                cmd += ["-isysroot", sdk]
        else:
            continue
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            first = (res.stderr or res.stdout).strip().splitlines()
            report.add(str(f), "clang-error",
                       "; ".join(first[:3]) or "compile failed")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def collect_classes(root: Path) -> List[Tuple[str, Path, Path]]:
    """配对 头文件/实现文件。返回 (lang, header, impl)。"""
    pairs: List[Tuple[str, Path, Path]] = []
    files = list(root.rglob("*")) if root.is_dir() else [root]
    by_stem: Dict[str, Dict[str, Path]] = {}
    for f in files:
        if f.suffix in (".h", ".hpp", ".m", ".cpp"):
            by_stem.setdefault(f.stem, {})[f.suffix] = f
    for stem, d in by_stem.items():
        header = d.get(".h") or d.get(".hpp")
        if ".cpp" in d and header:
            pairs.append(("cpp", header, d[".cpp"]))
        elif ".m" in d and header:
            pairs.append(("objc", header, d[".m"]))
    return pairs


def check_path(target: Path, report: Report, clang_files: List[Path]) -> None:
    for lang, header, impl in collect_classes(target):
        report.files_checked += 1
        if lang == "cpp":
            check_cpp_class(header, impl, report)
        else:
            check_oc_class(header, impl, report)
        clang_files.extend([header, impl])


def main(argv: List[str]) -> int:
    # Windows 控制台默认 GBK，强制 UTF-8 避免中文/符号编码崩溃
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    targets = [Path(a) for a in argv[1:]] or [Path(".")]
    report = Report()
    clang_files: List[Path] = []

    for t in targets:
        if not t.exists():
            print(f"  跳过不存在的路径：{t}")
            continue
        check_path(t, report, clang_files)

    run_clang(clang_files, report)

    print(f"\n校验类对数：{report.files_checked}")
    if report.ok:
        print("[OK] 结构校验全部通过")
        return 0

    # 按类型聚合
    by_kind: Dict[str, int] = {}
    for it in report.issues:
        by_kind[it.kind] = by_kind.get(it.kind, 0) + 1
    print(f"[FAIL] 发现 {len(report.issues)} 个问题：")
    for kind, n in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"   {kind}: {n}")
    print("\n示例（前 20 条）：")
    for it in report.issues[:20]:
        print(f"  [{it.kind}] {it.file}: {it.detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
