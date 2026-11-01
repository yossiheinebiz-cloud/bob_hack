"""Gate: project red lines from AGENTS.md / .bob/rules.
1. No secrets / API keys in tracked files.
2. No accusatory words in product UI or engine output ("חשד לבדיקה" only).
Run: python scripts/check_policy.py   (scans files tracked by git)
"""
import re
import subprocess
import sys

SECRET = re.compile(
    r"sk-(?:proj-|or-v1-|ant-)?[A-Za-z0-9_\-]{20,}"   # OpenAI / OpenRouter / Anthropic
    r"|AIza[0-9A-Za-z_\-]{35}"                        # Google
    r"|gh[pousr]_[A-Za-z0-9]{30,}"                    # GitHub
    r"|AKIA[0-9A-Z]{16}"                              # AWS access key id
    r"|xox[abpr]-[A-Za-z0-9-]{10,}"                   # Slack
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)
FORBIDDEN = re.compile(r"גניבה|הונאה|מרמה")
UI_PREFIXES = ("design/v2/", "engine/", "api/", "dashboard/")
# docs that define the rule itself are allowed to name the words
RULE_DOCS = ("AGENTS.md", "08-spec-v2.md", "design/v2/BRIEF.md", "scripts/check_policy.py")
SKIP_EXT = (".png", ".jpg", ".jpeg", ".pdf", ".pyc")


def main() -> int:
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    problems = []
    for path in filter(None, files):
        if path.endswith(SKIP_EXT) or path == ".env":
            if path == ".env":
                problems.append(".env is tracked by git")
            continue
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in SECRET.finditer(text):
            problems.append(f"{path}: possible secret '{m.group()[:8]}…'")
        if path.startswith(UI_PREFIXES) and path not in RULE_DOCS:
            for m in FORBIDDEN.finditer(text):
                problems.append(f"{path}: forbidden word '{m.group()}' (use 'חשד לבדיקה')")
    for p in problems:
        print("FAIL", p)
    print("POLICY CHECK PASSED" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
