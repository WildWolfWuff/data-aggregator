import ast
from collections.abc import Collection

from .errors import ScriptValidationError

DENIED_MODULES: frozenset[str] = frozenset({
  "sys", "os", "subprocess", "shutil", "socket", "ctypes", "importlib", "builtins", "pathlib",
  "pickle", "marshal", "multiprocessing", "threading", "signal", "http", "urllib", "requests",
  "httpx", "httpx2", "httpcore2", "inspect", "gc", "code", "codeop", "runpy", "pty", "tempfile", "webbrowser", "ftplib",
  "smtplib", "telnetlib", "posix", "nt", "io", "glob", "fileinput", "resource", "mmap", "pkgutil",
  "zipimport", "ssl", "select", "selectors", "asyncio",
})  # fmt: skip

DEFAULT_ALLOWED_MODULES: frozenset[str] = frozenset({
  "pandas", "numpy", "math", "re", "datetime", "json", "typing", "collections", "itertools",
  "functools", "decimal", "statistics", "string", "operator", "dataclasses", "enum", "__future__",
})  # fmt: skip

DENIED_CALLS: frozenset[str] = frozenset({
  "eval", "exec", "compile", "__import__", "open", "input", "breakpoint", "getattr", "setattr",
  "delattr", "globals", "locals", "vars", "memoryview",
})  # fmt: skip

PROCESS_FUNCTION_NAME = "aggregate_data"


def _check_module(name: str, lineno: int, allowed: Collection[str], violations: list[str]) -> None:
  root = name.split(".")[0]
  if root in DENIED_MODULES:
    violations.append(f"line {lineno}: import of '{name}' is not allowed")
  elif root not in allowed:
    violations.append(f"line {lineno}: import of '{name}' is not in the allowed modules")


def validate_script(source: str, allowed_modules: Collection[str] = DEFAULT_ALLOWED_MODULES) -> ast.Module:
  """Statically validate the script and return its AST.

  This is a best-effort filter and not a sandbox.
  """
  try:
    tree = ast.parse(source)
  except SyntaxError as e:
    raise ScriptValidationError([f"line {e.lineno}: syntax error: {e.msg}"]) from e

  violations: list[str] = []
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      for alias in node.names:
        _check_module(alias.name, node.lineno, allowed_modules, violations)
    elif isinstance(node, ast.ImportFrom):
      if node.level:
        violations.append(f"line {node.lineno}: relative imports are not allowed")
      else:
        _check_module(node.module or "", node.lineno, allowed_modules, violations)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in DENIED_CALLS:
      violations.append(f"line {node.lineno}: call to '{node.func.id}' is not allowed")
    elif isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr.endswith("__"):
      violations.append(f"line {node.lineno}: access to '{node.attr}' is not allowed")
    elif isinstance(node, ast.Name) and node.id in {"__builtins__", "__import__"}:
      violations.append(f"line {node.lineno}: use of '{node.id}' is not allowed")

  process_def = next(
    (n for n in tree.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) and n.name == PROCESS_FUNCTION_NAME),
    None,
  )
  if process_def is None:
    violations.append(f"script must define a top-level function '{PROCESS_FUNCTION_NAME}'")
  elif len(process_def.args.args) + len(process_def.args.posonlyargs) != 1:
    violations.append(f"'{PROCESS_FUNCTION_NAME}' must take exactly one parameter")

  if violations:
    raise ScriptValidationError(violations)
  return tree
