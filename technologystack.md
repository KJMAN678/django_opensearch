# 技術スタック

## コア技術
- python: 3.13
- OpenSearch: 2.17.1
- postgres:17

## Pythonのバージョン管理
- uv: 0.5.21

## Webアプリ
- Django: 5.1.4
- psycopg2-binary: 2.9.10
- django-environ: 0.12.0
- opensearch-py: 2.8.0

## 開発ツール
- opensearch-dashboards:2.17.1

## OpenSearch プラグイン
- Analysis-Sudachi: 3.3.0
---

# Django 検索画面
## 実装規則
- web/blog/views.py - OpenSearch の検索クエリの定義および実行
- web/search/documents.py  - OpenSearch のドキュメントの定義
- web/blog/templates/blog_list.html ... 実際に表示する検索画面のHTMLファイル
- web/blog/models.py - データベースに登録する Blog のテーブルを定義する
