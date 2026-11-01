"""Gate: every design/v2 page loads with no JS errors and no horizontal scroll at desktop + 390px.
Run: python scripts/check_design.py [--shots]   (--shots also refreshes design/v2/shots/*.png)
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent / "design" / "v2"
SHOTS = "--shots" in sys.argv
VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}


def main() -> int:
    pages = sorted(p.stem for p in ROOT.glob("*.html"))
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name in pages:
            for tag, (w, h) in VIEWPORTS.items():
                page = browser.new_page(viewport={"width": w, "height": h})
                errors = []
                page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
                page.goto((ROOT / f"{name}.html").as_uri() + ("#end" if name == "scanning" else ""))
                page.wait_for_timeout(1500)
                scroll_w = page.evaluate("document.documentElement.scrollWidth")
                if SHOTS:
                    page.screenshot(path=str(ROOT / "shots" / f"{name}-{tag}.png"), full_page=True)
                if errors:
                    failures.append(f"{name} [{tag}] JS error: {errors[0]}")
                if scroll_w > w:
                    failures.append(f"{name} [{tag}] horizontal scroll: {scroll_w}px > {w}px")
                page.close()
        browser.close()
    print(f"checked {len(pages)} pages x {len(VIEWPORTS)} viewports")
    for f in failures:
        print("FAIL", f)
    print("DESIGN CHECK PASSED" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
