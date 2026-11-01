"""Generate marketing images for design/v2/img/ (איפה הכסף).

Usage: python scripts/gen_images.py [name ...]   # no names = all
OpenAI gpt-image-1 first, Gemini fallback. Keys come from .env, never printed.
"""
import base64, io, os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "design" / "v2" / "img"

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

STYLE = (
    "Premium 3D product render, Apple-keynote / Stripe-level art direction. "
    "Near-black background #070B10, deep space-like darkness. Material language: "
    "polished translucent glass and frosted glass with subtle refraction, thin glowing edges. "
    "Palette strictly: emerald green #2EE6A8 (money found), electric blue #5B9DFF, "
    "soft violet #A78BFA (AI), warm amber #FFB547 (suspicious) used sparingly. "
    "Volumetric light, soft colored rim light, shallow depth of field, fine film grain, "
    "high-end cinematic, minimal, elegant, lots of negative space. "
    "Absolutely no text, no letters, no numbers, no digits, no symbols, no currency signs, "
    "no watermark, no brand logos, no UI labels."
)

IMAGES = {
    "hero": ("1536x1024", "3:2",
        "Cinematic wide dark 3D scene. A sleek translucent glass lens-shaped vault core floats in darkness, "
        "in the LEFT HALF of the frame (center of the core at about 35% of the width). From the far left, streams of glowing blue and violet data particles and "
        "thin translucent blank glass invoice cards flow into the core, among them small abstract glass glyphs "
        "(a cloud shape, a microchip shape, rounded app tiles). From the right side of the core, a short tight beam of "
        "condensed emerald light and a few solid glowing emerald glass coins (thick discs, blank faces) emerge and stay close to the core, "
        "ending before the middle of the frame. The RIGHT 40% of the frame is pure empty near-black #070B10 negative space, "
        "no smoke, no particles, only an extremely faint emerald gradient."),
    "login-art": ("1024x1536", "2:3",
        "Vertical abstract composition. Flowing ribbons of emerald and electric blue light curve to form a "
        "subtle magnifying-glass silhouette (a ring with a handle) floating above a perspective grid of faint, "
        "blank, ghostly receipt slips fading into darkness. Mostly dark, elegant, minimal."),
    "feat-ai": ("1024x1024", "1:1",
        "Single hero object centered: a glowing frosted-glass neural microchip with fine circuit veins, "
        "tiny violet token particles rising and orbiting around it, soft violet rim light, dark backdrop."),
    "feat-cloud": ("1024x1024", "1:1",
        "Single hero object centered: a frosted glass cloud shape with a row of slim glass server blades inside "
        "it glowing electric blue; exactly one blade in the middle is dark and lifeless, outlined in a strong warm amber #FFB547 glow, clearly different from the others, an idle 'zombie' server. Soft blue rim light."),
    "feat-saas": ("1024x1024", "1:1",
        "Single hero object centered: a neat stack of frosted glass seat cards (like membership passes, blank), "
        "most glowing emerald, a few hollow empty outline cards glowing amber to suggest unused seats. Soft emerald rim light."),
    "feat-receipts": ("1024x1024", "1:1",
        "Single hero object centered: two identical tall paper-like frosted glass receipts with zig-zag torn top and bottom edges, "
        "each with the same pattern of faint horizontal placeholder bars, overlapping slightly and offset; "
        "a thin horizontal emerald scan beam passes across them revealing they are duplicates, with a faint "
        "amber outline on the copy. Soft emerald rim light. Receipts have only abstract faint lines, no characters."),
    "integrations-orbit": ("1536x1024", "3:2",
        "Wide dark space. At center a glowing emerald spherical core. Around it, seven small frosted glass "
        "rounded tiles orbit on thin elliptical light paths, each tile with a simple abstract glowing glyph: "
        "a bank building, a cloud, a chat bubble, a document, a microchip, a phone, a lightning bolt. "
        "Thin luminous lines connect each tile to the core. Blue and violet accents."),
    "mobile-hero": ("1024x1536", "2:3",
        "A modern thin bezel-less smartphone floating at a dynamic angle in darkness with rim lighting. "
        "Its screen shows an abstract dark finance app: one large glowing emerald rounded bar shape at top "
        "and several stacked dark glass cards with colored accent dots (amber, blue, violet) and blank placeholder "
        "bars instead of text. No legible text anywhere. Emerald glow reflecting on the phone edges."),
    "empty-state": ("1024x1024", "1:1",
        "Calm minimal still life: a single elegant glass magnifying glass resting on a dark matte surface, "
        "faint emerald glow inside the lens and a soft reflection below. Quiet, lots of empty space."),
}


def gen_openai(prompt, size):
    from openai import OpenAI
    r = OpenAI().images.generate(model="gpt-image-1", prompt=prompt, size=size, quality="high", n=1)
    return base64.b64decode(r.data[0].b64_json), "gpt-image-1"


def gen_openrouter(prompt, aspect, model=os.environ.get("OR_IMG_MODEL", "google/gemini-3-pro-image")):
    import requests
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=300,
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]},
        json={"model": model, "modalities": ["image", "text"],
              "image_config": {"aspect_ratio": aspect},
              "messages": [{"role": "user", "content": "Generate an image. " + prompt}]})
    r.raise_for_status()
    url = r.json()["choices"][0]["message"]["images"][0]["image_url"]["url"]
    return base64.b64decode(url.split(",", 1)[1]), "openrouter:" + model


def gen_gemini(prompt, aspect):
    from google import genai
    from google.genai import types
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    try:
        r = c.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt,
                                     config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=aspect))
        return r.generated_images[0].image.image_bytes, "imagen-4.0-generate-001"
    except Exception as e:
        print("  imagen failed:", type(e).__name__)
    r = c.models.generate_content(model="gemini-2.5-flash-image", contents=prompt + f" Aspect ratio {aspect}.")
    for p in r.candidates[0].content.parts:
        if p.inline_data:
            return p.inline_data.data, "gemini-2.5-flash-image"
    raise RuntimeError("gemini returned no image")


def save(name, data):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((1600, 1600), Image.LANCZOS)  # web size, keeps aspect
    im.save(OUT / f"{name}.png", optimize=True)
    return im


def make_og():
    im = Image.open(OUT / "hero.png")
    w, h = im.size
    ch = int(w * 630 / 1200)  # center crop to 1.91:1
    top = (h - ch) // 2
    im.crop((0, top, w, top + ch)).resize((1200, 630), Image.LANCZOS).save(OUT / "og.png", optimize=True)


def one(name):
    size, aspect, subject = IMAGES[name]
    prompt = subject + " " + STYLE
    for fn, arg in ((gen_openai, size), (gen_openrouter, aspect), (gen_gemini, aspect)):
        try:
            data, model = fn(prompt, arg)
            break
        except Exception as e:  # ponytail: type only, error bodies can echo masked keys
            print(f"{name}: {fn.__name__} failed ({type(e).__name__})")
    else:
        raise RuntimeError(f"{name}: all providers failed")
    save(name, data)
    print(f"{name}: ok via {model}")
    return name, model


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(IMAGES)
    with ThreadPoolExecutor(4) as ex:
        for f in [ex.submit(one, n) for n in names if n != "og"]:
            try:
                f.result()
            except Exception as e:
                print("FAILED:", e)
    if (OUT / "hero.png").exists() and ("hero" in names or "og" in names):
        make_og()
        print("og: ok (crop of hero)")
