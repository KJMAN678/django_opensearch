# blog/views.py 130-200行目 解説

この部分のコードは、**時間ベースの関連キーワード検索機能**を実装しています。

## 処理の流れ

### 1. 検索ワードの分割 (130-132行目)
```python
search_words = search_word.split()
all_time_based_results = []
```
- 入力された検索ワードをスペースで分割し、複数単語に対応
- 結果を格納するリストを初期化

### 2. 各単語の検索時間を取得 (134-150行目)
```python
word_timestamps = {}
for word in search_words:
    searched_at_response = client.search(...)
```
- 各単語について、過去に検索された時間（`searched_at`）を全て取得
- OpenSearchの`search_log`インデックスから該当する検索ログを抽出
- 結果を`word_timestamps`辞書に格納

### 3. 共通の検索時間帯を特定 (152-155行目)
```python
common_timestamps = set(word_timestamps[search_words[0]])
for word in search_words[1:]:
    common_timestamps &= set(word_timestamps[word])
```
- 複数の検索ワードが**同じ時間帯**に検索された時間を特定
- 集合の積演算（`&=`）を使って共通する時間帯のみを抽出

### 4. 関連キーワードの集計 (157-195行目)
```python
if common_timestamps:
    agg_response = client.search(...)
```
- 共通の時間帯が存在する場合のみ実行
- その時間帯に検索された**他の検索クエリ**を集計
- `must_not`で元の検索ワードは除外
- 出現回数順で上位10件を取得

### 5. 結果の整理 (197-199行目)
```python
time_based_results = sorted(
    all_time_based_results, key=lambda x: x["count"], reverse=True
```
- 集計結果を出現回数の降順でソート

## 目的

この機能は、**同じタイミングで検索された関連性の高いキーワード**を発見することで、ユーザーの検索意図をより深く理解し、より適切な関連キーワードを提案することを目的としています。