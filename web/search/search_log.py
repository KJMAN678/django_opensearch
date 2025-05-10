from opensearchpy import OpenSearch
import environ
from search.documents import PastSearchLogDocument
from datetime import datetime
import uuid


def search_log(search_word):
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
