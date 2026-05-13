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
├── templates/
│   └── dashboard-v1.html.tmpl       # Jinja2用テンプレート（Claude Skill で使用）
└── docs/                            # GitHub Pages 公開ディレクトリ
    ├── index.html                   # レポート一覧ページ
    └── reports/
        └── {SYMBOL}_{YYYYMMDD}.html # レポート詳細ページ
```

## 技術スタック

- HTML / CSS / JavaScript
  - [Chart.js](https://www.chartjs.org/)
- Claude Skill
  - Jinja2
