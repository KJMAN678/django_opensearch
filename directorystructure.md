/
├── LICENSE                       # ライセンスファイル
├── README.md                     # プロジェクト説明
├── container_remake.sh           # コンテナ再作成スクリプト
├── directorystructure.md         # ディレクトリ構造説明
├── docker-compose.yml            # Docker Compose設定
├── generate_certs.sh             # 証明書生成スクリプト
├── init-security.sh              # セキュリティ初期化スクリプト
├── initialize_script.sh          # 初期化スクリプト
├── technologystack.md            # 技術スタック説明
├── opensearch/                   # OpenSearchコンテナ設定
│   ├── Dockerfile                # OpenSearch Dockerファイル
│   ├── backup/                   # バックアップファイル格納
│   ├── config/                   # OpenSearch設定
│   │   ├── certs/                # SSL証明書
│   │   └── opensearch.yml        # OpenSearch設定ファイル
│   ├── opensearch-security/      # セキュリティ設定
│   │   ├── action_groups.yml     # アクショングループ設定
│   │   ├── config.yml            # セキュリティ設定
│   │   ├── internal_users.yml    # 内部ユーザー設定
│   │   ├── roles.yml             # ロール設定
│   │   ├── roles_mapping.yml     # ロールマッピング設定
│   │   └── tenants.yml           # テナント設定
│   └── synonyms.txt              # 同義語辞書
└── web/                          # Django Webアプリケーション
    ├── Dockerfile                # Django Dockerファイル
    ├── manage.py                 # Django管理スクリプト
    ├── pyproject.toml            # Python依存関係設定
    ├── uv.lock                   # 依存関係ロックファイル
    ├── config/                   # Django設定
    │   ├── __init__.py
    │   ├── asgi.py               # ASGI設定
    │   ├── settings.py           # Django設定
    │   ├── urls.py               # URLルーティング
    │   └── wsgi.py               # WSGI設定
    ├── blog/                     # ブログアプリケーション
    │   ├── __init__.py
    │   ├── admin.py              # Django管理画面設定
    │   ├── apps.py               # アプリ設定
    │   ├── forms.py              # フォーム定義
    │   ├── models.py             # データモデル
    │   ├── tests.py              # テスト
    │   ├── urls.py               # URLパターン
    │   ├── views.py              # ビュー関数
    │   ├── management/           # カスタム管理コマンド
    │   │   └── commands/
    │   │       ├── __init__.py
    │   │       └── register_fake_blog_model.py
    │   ├── migrations/           # データベースマイグレーション
    │   │   ├── 0001_initial.py
    │   │   └── __init__.py
    │   └── templates/            # テンプレートファイル
    │       └── blog_list.html
    └── search/                   # 検索機能アプリケーション
        ├── __init__.py
        ├── documents.py          # OpenSearch文書定義
        ├── search_log.py         # 検索ログ機能
        └── management/           # 検索関連管理コマンド
            └── commands/
                ├── init_index.py      # インデックス初期化
                ├── make_backup.py     # バックアップ作成
                ├── restore_backup.py  # バックアップリストア
                └── search.py          # 検索実行