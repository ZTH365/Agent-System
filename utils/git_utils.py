import subprocess
from typing import Optional


def run_git_command(cmd):
    """执行 git 命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {' '.join(cmd)}\n{e.stderr}")


def is_git_repo() -> bool:
    """检查是否在 git 仓库中"""
    try:
        run_git_command(["git", "rev-parse", "--is-inside-work-tree"])
        return True
    except:
        return False


def get_git_diff(
    base: Optional[str] = "HEAD~1",
    target: Optional[str] = "HEAD",
    max_chars: int = 8000,
    ignore_whitespace: bool = True
) -> str:
    """
    获取 git diff

    参数：
    - base: 起始 commit / 分支
    - target: 目标 commit / 分支
    - max_chars: 最大返回长度（防止 LLM 超长）
    - ignore_whitespace: 是否忽略空白变化
    """

    if not is_git_repo():
        raise RuntimeError("当前目录不是 Git 仓库")

    cmd = ["git", "diff", base, target]

    if ignore_whitespace:
        cmd.append("-w")

    # 只显示变更文件名（可选扩展点）
    # cmd.append("--name-only")

    diff = run_git_command(cmd)

    if not diff:
        return ""

    # 裁剪超长 diff（关键工程优化）
    if len(diff) > max_chars:
        diff = diff[:max_chars]
        diff += "\n\n... (diff truncated)"

    return diff
    
def filter_diff(diff: str) -> str:
    keywords = [".py", ".java", ".go", ".js"]

    lines = diff.split("\n")
    filtered = []

    keep = False
    for line in lines:
        if line.startswith("diff --git"):
            keep = any(k in line for k in keywords)

        if keep:
            filtered.append(line)

    return "\n".join(filtered)
