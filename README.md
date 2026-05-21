# finance-reports

Claude Skill で生成した金融レポートを保管・公開するリポジトリです。

## 公開 URL

<https://tw398must-cell.github.io/finance-reports>

## 概要

GitHub Pages により静的サイトとして公開しています。
`main` ブランチに HTML ファイルを push すると自動的にサイトへ反映されます。

## ディレクトリ構成

```text
.
├── .github/workflows/
│   └── build-manifest.yml           # reports.json を自動再生成する CI
├── templates/
│   └── dashboard-v1.x.html.tmpl     # Jinja2用テンプレート（Claude Skill で使用）
├── scripts/
│   └── build_manifest.py            # docs/reports.json を生成するスクリプト
└── docs/                            # GitHub Pages 公開ディレクトリ
    ├── index.html                   # レポート一覧ページ
    ├── reports.json                 # 一覧ページ用メタ情報目録（自動生成）
    └── reports/
        └── {SYMBOL}_{YYYYMMDD}.html # レポート詳細ページ
```

- 一覧ページ`docs/index.html` のテーブル構成は、SYMBOL / SECTOR / FEATURE / RATE / DATETIME
  - 目録`docs/reports.json` を読み込んで描画する。
    - 生成は HTML を push するだけでよい。
      - (**GitHub Actions**) 新しいレポートが push されると、`reports.json` を再生成・コミットする。
    - 手元で再構築する場合は`python3 scripts/build_manifest.py` を実行する。

## 技術スタック

- HTML / CSS / JavaScript
  - [Chart.js](https://www.chartjs.org/)
- Claude Skill
  - Jinja2
