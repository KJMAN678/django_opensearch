from django.shortcuts import render
from django.views.generic import ListView, FormView
from blog.models import Blog
from blog.forms import SearchWordForm
from django.urls import reverse_lazy
from opensearchpy import OpenSearch
import environ
from search.documents import BlogDocument

class BlogListView(FormView):
    template_name = 'blog_list.html'
    form_class = SearchWordForm
    success_url = reverse_lazy('blog_list')  # 名前付きURLを指定

    def form_valid(self, form):
        # フォームから検索ワードを取得
        search_word = form.cleaned_data.get('search_word')

        # 検索ロジックを実行（例: BlogPostのタイトルを検索）
        posts = self.search(search_word)

        # フォームと検索結果をテンプレートに渡す
        return render(self.request, self.template_name, {
            'form': form,
            'posts': posts,
        })

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def search(self, search_word):

        host = 'opensearch'
        port = 9200

        env = environ.Env()
        environ.Env.read_env(".env")
        OPENSEARCH_INITIAL_ADMIN_PASSWORD = env('OPENSEARCH_INITIAL_ADMIN_PASSWORD')
        auth = ('admin', OPENSEARCH_INITIAL_ADMIN_PASSWORD)

        client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
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
                "query": {
                    "match": {
                        "title": search_word
                    }
                }
            }
        )

        if response["hits"]["hits"]:
            posts = []
            for hit in response["hits"]["hits"]:
                post = {
                    'title': hit["_source"]["title"],
                    'content': hit["_source"]["content"],
                }
                posts.append(post)
            return posts
        else:
            return None
