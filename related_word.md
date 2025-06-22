# blog/views.py 時間ベースの関連キーワード検索機能 解説

この部分のコードは、**時間・ユーザーベースの関連キーワード検索機能**を実装しています。

## 処理の流れ

### 1. 検索ワードの分割と初期化 (157-159行目)
```python
search_words = search_word.split()
all_time_based_results = []
```
- 入力された検索ワードをスペースで分割し、複数単語に対応
- 結果を格納するリストを初期化

### 2. 各単語の検索時間とユーザーIDを取得 (162-184行目)
```python
word_timestamps_and_users = {}
for word in search_words:
    searched_at_response = client.search(
        index="search_log",
        body={
            "query": {"term": {"search_query": word}},
            "size": 1000,
            "_source": ["searched_at", "user_id"],
        },
    )
```
- 各単語について、過去に検索された時間（`searched_at`）と検索したユーザー（`user_id`）を全て取得
- OpenSearchの`search_log`インデックスから該当する検索ログを抽出
- 重複排除のためsetを使用し、`(timestamp, user_id)`のタプルのセット形式で格納

### 3. 共通の検索時間帯・ユーザーを特定 (186-189行目)
```python
common_timestamps_and_users = set(word_timestamps_and_users[search_words[0]])
for word in search_words[1:]:
    common_timestamps_and_users &= set(word_timestamps_and_users[word])
```
- 複数の検索ワードが**同じ時間帯**かつ**同じユーザー**によって検索された時間とユーザーの組み合わせを特定
- 集合の積演算（`&=`）を使って共通する時間・ユーザーの組み合わせのみを抽出

### 4. 関連キーワードの集計 (191-244行目)
```python
if common_timestamps_and_users:
    agg_response = client.search(
        index="search_log",
        body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "bool": {
                                            "must": [
                                                {"term": {"searched_at": timestamp}},
                                                {"term": {"user_id": user_id}},
                                            ]
                                        }
                                    }
                                    for timestamp, user_id in common_timestamps_and_users
                                ]
                            }
                        }
                    ],
                    "must_not": [{"terms": {"search_query": search_words}}],
                }
            },
            "aggs": {
                "related_queries": {
                    "terms": {
                        "field": "search_query",
                        "size": 10,
                        "order": {"_count": "desc"},
                    }
                }
            },
        },
    )
```
- 共通の時間・ユーザーの組み合わせが存在する場合のみ実行
- その時間・ユーザーの組み合わせで検索された**他の検索クエリ**を集計
- `must_not`で元の検索ワードは除外
- 出現回数順で上位10件を取得

### 5. 結果の整理 (247-263行目)
```python
for bucket in agg_response["aggregations"]["related_queries"]["buckets"]:
    all_time_based_results.append(
        {
            "word": bucket["key"],
            "count": bucket["doc_count"],
            "timestamp": list(common_timestamps_and_users)[0][0]
            if common_timestamps_and_users
            else None,
        }
    )

time_based_results = sorted(
    all_time_based_results, key=lambda x: x["count"], reverse=True
)[:10]
```
- 集計結果を出現回数の降順でソート
- 上位10件のみ表示

## 機能の改善点

従来の時間ベース検索から、**時間・ユーザーベース検索**に改善されています：

1. **ユーザー情報の追加**: 検索時間だけでなく、検索したユーザーIDも考慮
2. **精度向上**: 同じユーザーが同じ時間帯に検索した場合のみ関連性があると判定
3. **誤検知の削減**: 異なるユーザーが偶然同じ時間に検索したケースを排除

## 目的

この機能は、**同じユーザーが同じタイミングで検索した関連性の高いキーワード**を発見することで、ユーザーの検索意図をより正確に理解し、より適切な関連キーワードを提案することを目的としています。