from django.shortcuts import render
from django.views.generic import FormView
from blog.forms import SearchWordForm
from django.urls import reverse_lazy
from opensearchpy import OpenSearch
import environ
from search.documents import BlogDocument


class BlogListView(FormView):
    template_name = "blog_list.html"
    form_class = SearchWordForm
    success_url = reverse_lazy("blog_list")  # 名前付きURLを指定

    def form_valid(self, form):
        # フォームから検索ワードを取得
        search_word = form.cleaned_data.get("search_word")

        # 検索ロジックを実行
        posts, suggestions = self.search(search_word)

        # フォームと検索結果をテンプレートに渡す
        return render(
            self.request,
            self.template_name,
            {
                "form": form,
                "posts": posts,
                "suggestions": suggestions,
            },
        )

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})

    def get_suggestions(self, search_word):
        # サジェスト用の検索ロジック
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

        # サジェスト用の検索クエリ
        response = client.search(
            index=BlogDocument._index._name,
            body={
                "query": {
                    "multi_match": {
                        "query": search_word,
                        "fields": ["title^2", "content"],
                        "fuzziness": "AUTO",
                    }
                },
                "size": 5,  # サジェストの数を制限
            },
        )

        if response["hits"]["hits"]:
            suggestions = []
            for hit in response["hits"]["hits"]:
                suggestion = {"title": hit["_source"]["title"], "score": hit["_score"]}
                suggestions.append(suggestion)
            return suggestions
        return None

    def search(self, search_word):
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

        # データの検索
        response = client.search(
            index=BlogDocument._index._name,
            body={
                "query": {"match": {"title": search_word}},
                "suggest": {
                    "title_suggest": {
                        "prefix": search_word,
                        "completion": {"field": "title_suggest", "size": 5},
                    }
                },
            },
        )

        posts = []
        suggestions = []

        if response["hits"]["hits"]:
            for hit in response["hits"]["hits"]:
                post = {
                    "title": hit["_source"]["title"],
                    "content": hit["_source"]["content"],
                }
                posts.append(post)

        if response["suggest"]:
            for option in response["suggest"]["title_suggest"][0]["options"]:
                suggestion = {"title": option["text"]}
                suggestions.append(suggestion)

        return posts, suggestions
