"""Create placeholder PNGs for EXERCISE.md filenames.

Replace these files with real Braintrust dashboard screenshots before grading if required.
Run from repo root:

    cd simple-agent-observability && uv run python generate_braintrust_placeholders.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _draw_card(path: Path, title: str, lines: tuple[str, ...]) -> None:
    w, h = 920, 520
    img = Image.new("RGB", (w, h), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
        font_body = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
    except OSError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.rectangle((20, 20, w - 20, h - 20), outline=(100, 120, 160), width=3)
    y = 48
    draw.text((48, y), title, fill=(20, 30, 50), font=font_title)
    y += 52
    for line in lines:
        draw.text((48, y), line, fill=(40, 50, 70), font=font_body)
        y += 32
    img.save(path, format="PNG")


def main() -> None:
    here = Path(__file__).resolve().parent

    _draw_card(
        here / "braintrust-overview.png",
        "Placeholder: Braintrust Logs overview",
        (
            "Replace with a screenshot of the Logs view showing multiple traces.",
            "Tip: run OBSERVABILITY_BATCH=1 then open braintrust.dev -> Logs.",
        ),
    )
    _draw_card(
        here / "braintrust-trace-details.png",
        "Placeholder: Single trace / spans",
        (
            "Replace with one trace expanded to show spans (model + tool calls).",
        ),
    )
    _draw_card(
        here / "braintrust-metrics.png",
        "Placeholder: Metrics (tokens / latency)",
        (
            "Replace with a Braintrust view showing token usage or latency.",
        ),
    )
    _draw_card(
        here / "braintrust-mcp-tool.png",
        "Placeholder: MCP tool in trace",
        (
            "Replace after asking a doc question that uses Context7 MCP tools.",
            "Run with MCP enabled; capture span that shows MCP tool invocation.",
        ),
    )
    print("Wrote PNG placeholders in", here)


if __name__ == "__main__":
    main()
