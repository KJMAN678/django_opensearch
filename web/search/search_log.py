from opensearchpy import OpenSearch
import environ
from search.documents import (
    PastSearchLogDocument,
    RelatedSearchWordLogDocument,
    NoOrderRelatedSearchWordLogDocument,
    AggPastSearchLogDocument,
    PermutationSearchWordLogDocument,
)
from datetime import datetime
import uuid


def make_client():
    host = "opensearch"
    port = 9200

    env = environ.Env()
    environ.Env.read_env(".env")
    OPENSEARCH_INITIAL_ADMIN_PASSWORD = env("OPENSEARCH_INITIAL_ADMIN_PASSWORD")
    auth = ("admin", OPENSEARCH_INITIAL_ADMIN_PASSWORD)

    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    return client


def search_log(search_word):
    """過去の検索ログを保存する"""
    client = make_client()
    from search.documents import SearchLogDocument
    import time

    # past_search_logインデックスを作成
    if not client.indices.exists(index="past_search_log"):
        PastSearchLogDocument.init(using=client, index="past_search_log")

    response = client.search(
        index="past_search_log",
        body={"query": {"match": {"search_word": search_word}}},
    )

    if not response["hits"]["hits"]:
        doc = PastSearchLogDocument(
            id=uuid.uuid4(),
            user_id=1,
            search_word=search_word,
            created_at=datetime.now(),
        )
        doc.save(using=client, index="past_search_log")

    # search_logインデックスにも保存（時間ベース検索用）
    if not client.indices.exists(index="search_log"):
        SearchLogDocument.init(using=client, index="search_log")

    # 現在時刻のUNIX時間
    current_timestamp = int(time.time())

    search_log_doc = SearchLogDocument(
        id=str(uuid.uuid4()),
        user_id="1",  # Keywordフィールドなので文字列
        search_query=search_word,
        searched_at=current_timestamp,
    )
    search_log_doc.save(using=client, index="search_log")


def split_search_and_related_keywords(sentence):
    words = sentence.split(" ")

    if len(words) <= 1:
        # 1要素以下の場合
        search_word = sentence
        related_word = ""
    else:
        # 2要素以上の場合
        search_word = " ".join(words[0:-1])  # 最後の要素を除く全て
        related_word = words[-1]  # 最後の要素

    return search_word, related_word


def agg_past_search_log(search_word):
    client = make_client()

    if not client.indices.exists(index="agg_past_search_log"):
        AggPastSearchLogDocument.init(using=client, index="agg_past_search_log")

    doc = AggPastSearchLogDocument(
        id=uuid.uuid4(),
        user_id=1,
        search_original_word=search_word,
        search_word=" ".join(search_word.split(" ")[:-1]),
        related_search_word=search_word.split(" ")[-1],
        created_at=datetime.now(),
    )
    doc.save(using=client, index="agg_past_search_log")


def related_search_word_log(search_word):
    # 関連の検索ワードを保存
    client = make_client()

    # インデックスを作成
    if not client.indices.exists(index="related_search_word_log"):
        RelatedSearchWordLogDocument.init(using=client, index="related_search_word_log")

    # 単純化して、スペース区切りで２つの検索ワードのみ対応する
    if len(search_word.split(" ")) == 1:
        return
    else:
        combinations = create_combinations(search_word)

        for combo in combinations:
            related_search_word = combo[0]
            query = " ".join(combo[1])
            id = query + related_search_word

            # ドキュメントがなければ count　を 1で作成、すでにあれば count を 1 増やす
            client.update(
                id=id,
                index="related_search_word_log",
                body={
                    "script": {
                        "source": "ctx._source.count += 1",
                        "lang": "painless",
                    },
                    "upsert": {
                        "search_query": query,
                        "related_search_word": related_search_word,
                        "count": 1,
                    },
                },
            )


def create_combinations(string):
    # 空白で区切ってリスト化
    arr = string.split()
    result = []
    for i in range(len(arr)):
        current = arr[i]
        rest = arr[:i] + arr[i + 1 :]
        result.append((current, rest))
    return result


def no_order_related_search_word_log(search_word):
    # ワードの順番を考慮しない、関連の検索ワードを保存
    client = make_client()

    # インデックスを作成
    if not client.indices.exists(index="no_order_related_search_word_log"):
        NoOrderRelatedSearchWordLogDocument.init(
            using=client, index="no_order_related_search_word_log"
        )

    # 単純化して、スペース区切りで２つの検索ワードのみ対応する
    if len(search_word.split(" ")) == 1:
        return
    else:
        related_search_word = search_word.split(" ")[-1]
        query = " ".join(search_word.split(" ")[:-1])
        id = query + related_search_word

        # ドキュメントがなければ count　を 1で作成、すでにあれば count を 1 増やす
        client.update(
            id=id,
            index="no_order_related_search_word_log",
            body={
                "script": {
                    "source": "ctx._source.count += 1",
                    "lang": "painless",
                },
                "upsert": {
                    "search_query": query,
                    "related_search_word": related_search_word,
                    "count": 1,
                },
            },
        )


def generate_factorial_permutations(search_words):
    """Generate all factorial permutations for search terms"""
    import itertools
    all_perms = []
    
    for r in range(1, len(search_words)):
        for perm in itertools.permutations(search_words, r):
            remaining = [w for w in search_words if w not in perm]
            if remaining:
                search_query = " ".join(perm)
                related_word = " ".join(remaining)
                all_perms.append((search_query, related_word))
    
    return all_perms


def permutation_search_word_log(search_word):
    """順列を考慮した関連検索ワードを保存"""
    client = make_client()
    
    # インデックスを作成
    if not client.indices.exists(index="permutation_search_word_log"):
        PermutationSearchWordLogDocument.init(using=client, index="permutation_search_word_log")
    
    words = search_word.split()
    if len(words) <= 1:
        return
    
    permutations = generate_factorial_permutations(words)
    
    for i, (query, related) in enumerate(permutations):
        doc_id = f"{search_word}_{query}_{related}".replace(" ", "_")
        
        # ドキュメントがなければ count を 1で作成、すでにあれば count を 1 増やす
        client.update(
            id=doc_id,
            index="permutation_search_word_log",
            body={
                "script": {
                    "source": "ctx._source.count += 1",
                    "lang": "painless",
                },
                "upsert": {
                    "original_search_query": search_word,
                    "search_query": query,
                    "related_search_word": related,
                    "permutation_order": i + 1,
                    "count": 1,
                },
            },
        )
