from opensearchpy import OpenSearch
import environ
from search.documents import PastSearchLogDocument
from datetime import datetime
import uuid


def search_log(search_word):
    """過去の検索ログを保存する"""
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

    # インデックスを作成
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


def related_search_word_log(search_word):
    # 関連の検索ワードを保存
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

    # インデックスを作成
    if not client.indices.exists(index="related_search_word_log"):
        PastSearchLogDocument.init(using=client, index="related_search_word_log")

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
