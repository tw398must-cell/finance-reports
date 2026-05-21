#!/usr/bin/env python3
"""docs/reports/*.html を走査して docs/reports.json を生成する。

各レポートHTMLからメタ情報（filename / name / symbol / sector / feature /
rate / datetime）を抽出し、一覧ページ docs/index.html が読み込む目録ファイルを作る。

通常運用では docs/reports/ への push をトリガに GitHub Actions
(.github/workflows/build-manifest.yml) がこのスクリプトを実行して
reports.json を再生成・コミットする。手元での再構築にも使える。

実行: python3 scripts/build_manifest.py
"""

import html
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "docs" / "reports"
OUTPUT = ROOT / "docs" / "reports.json"

FILENAME_RE = re.compile(r"^(?P<symbol>.+)_(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2})\.html$")
REPORT_TITLE_RE = re.compile(r'class="report-title">\s*(.*?)\s*</h1>', re.S)
REPORT_META_RE = re.compile(r'class="report-meta">\s*(.*?)\s*</div>', re.S)
MARKET_DESC_RE = re.compile(r'class="market-description">\s*(.*?)\s*</p>', re.S)
RATE_RE = re.compile(r'star-rate"\s+title="Rate:\s*(\d+)\s*/\s*5"')
# <meta name="generated-at" content="..."> — レポート生成スキルが埋め込む生成時刻。
GENERATED_AT_META_RE = re.compile(
    r'<meta\s+name="generated-at"\s+content="([^"]*)"', re.I
)
# footer の "Generated YYYY-MM-DD [HH:MM[:SS]] JST" — 旧レポート用フォールバック。
GENERATED_RE = re.compile(
    r"Generated\s+(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}(?::\d{2})?))?\s+JST"
)

FEATURE_MAX = 120


def strip_tags(text: str) -> str:
    """HTMLタグ・実体参照・余分な空白を除去してプレーンテキスト化する。"""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, limit: int = FEATURE_MAX) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def parse_report(path: Path) -> dict | None:
    name_match = FILENAME_RE.match(path.name)
    if not name_match:
        return None

    symbol = name_match.group("symbol")
    report_date = f"{name_match.group('y')}-{name_match.group('m')}-{name_match.group('d')}"
    content = path.read_text(encoding="utf-8")

    # name: 会社名（レポートタイトル）。取れなければシンボルで代用。
    title_match = REPORT_TITLE_RE.search(content)
    name = strip_tags(title_match.group(1)) if title_match else symbol

    # sector: report-meta の " · " 区切り後半
    sector = None
    meta_match = REPORT_META_RE.search(content)
    if meta_match:
        meta_text = strip_tags(meta_match.group(1))
        if "·" in meta_text:
            sector = meta_text.split("·", 1)[1].strip() or None

    # feature: 概況サマリ冒頭
    feature = ""
    desc_match = MARKET_DESC_RE.search(content)
    if desc_match:
        feature = truncate(strip_tags(desc_match.group(1)))

    # rate: star-rate の title 属性
    rate = None
    rate_match = RATE_RE.search(content)
    if rate_match:
        rate = int(rate_match.group(1))

    # datetime の決定:
    #   1. <meta name="generated-at">（生成スキルが埋め込む正確な時刻）
    #   2. footer の "Generated" 日付（旧レポート） + 00:00:00
    #   3. いずれも無ければファイル名の日付 + 00:00:00
    meta_at = GENERATED_AT_META_RE.search(content)
    if meta_at and meta_at.group(1).strip():
        dt = meta_at.group(1).strip()
    else:
        gen_match = GENERATED_RE.search(content)
        date_str = gen_match.group(1) if gen_match else report_date
        time_str = gen_match.group(2) if gen_match else None
        if time_str and len(time_str) == 5:  # "HH:MM" → "HH:MM:SS"
            time_str += ":00"
        dt = f"{date_str}T{time_str or '00:00:00'}+09:00"

    return {
        "filename": path.name,
        "name": name,
        "symbol": symbol,
        "sector": sector,
        "feature": feature,
        "rate": rate,
        "datetime": dt,
    }


def main() -> None:
    reports = []
    for path in sorted(REPORTS_DIR.glob("*.html")):
        entry = parse_report(path)
        if entry is None:
            print(f"skip (ファイル名が規約外): {path.name}")
            continue
        reports.append(entry)

    reports.sort(key=lambda r: r["datetime"], reverse=True)

    manifest = {
        "generated_at": datetime.now(JST).isoformat(timespec="seconds"),
        "reports": reports,
    }
    OUTPUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(reports)} reports)")


if __name__ == "__main__":
    main()
