from django.shortcuts import render
from django.views.generic import FormView
from blog.forms import SearchWordForm
from django.urls import reverse_lazy
from search.search_log import (
    make_client,
    search_log,
    related_search_word_log,
    no_order_related_search_word_log,
    agg_past_search_log,
)


class BlogListView(FormView):
    template_name = "blog_list.html"
    form_class = SearchWordForm
    success_url = reverse_lazy("blog_list")  # 名前付きURLを指定

    def form_valid(self, form):
        # フォームから検索ワードを取得
        search_word = form.cleaned_data.get("search_word")

        # 過去の検索ログをインデックスに保存
        search_log(search_word)

        # 集計対象にするための検索ログを保存
        agg_past_search_log(search_word)

        # 関連の検索ワードを取得
        related_search_word_log(search_word)

        # ワードの順番を考慮しない、関連の検索ワードを取得
        no_order_related_search_word_log(search_word)

        # 検索ロジックを実行
        (
            posts,
            suggestions,
            past_search_logs,
            agg_past_search_logs,
            related_search_word_logs,
            no_order_related_search_word_logs,
            title_aggression_keywords,
            past_search_aggregated_logs,
            time_based_results,
        ) = self.search(search_word)

        # フォームと検索結果をテンプレートに渡す
        return render(
            self.request,
            self.template_name,
            {
                "form": form,
                "posts": posts,
                "suggestions": suggestions,
                "past_search_logs": past_search_logs,
                "agg_past_search_logs": agg_past_search_logs,
                "related_search_word_logs": related_search_word_logs,
                "no_order_related_search_word_logs": no_order_related_search_word_logs,
                "title_aggression_keywords": title_aggression_keywords,
                "past_search_aggregated_logs": past_search_aggregated_logs,
                "time_based_results": time_based_results,
            },
        )

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})

    def get_suggestions(self, search_word):
        # サジェスト用の検索ロジック
        client = make_client()

        # サジェスト用の検索クエリ
        response = client.search(
            index="blog",
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
        client = make_client()

        # データの検索
        response = client.search(
            index="blog",
            body={
                "query": {"match": {"title": search_word}},
                "size": 1,
                "suggest": {
                    "title_suggest": {
                        "prefix": search_word,
                        "completion": {"field": "title_suggest", "size": 5},
                    }
                },
            },
        )

        # 同じ時間帯の検索ワードを集計
        time_based_search_response = client.search(
            index="past_search_log",
            body={
                "aggs": {
                    "search_times": {
                        "filter": {"term": {"search_word": search_word}},
                        "aggs": {
                            "timestamps": {
                                "terms": {"field": "created_at", "size": 1000},
                                "aggs": {
                                    "related_searches": {
                                        "reverse_nested": {},
                                        "aggs": {
                                            "same_time_searches": {
                                                "filter": {
                                                    "bool": {
                                                        "must": [
                                                            {
                                                                "term": {
                                                                    "created_at": "{{timestamp}}"
                                                                }
                                                            },
                                                            {
                                                                "bool": {
                                                                    "must_not": [
                                                                        {
                                                                            "term": {
                                                                                "search_word": search_word
                                                                            }
                                                                        }
                                                                    ]
                                                                }
                                                            },
                                                        ]
                                                    }
                                                },
                                                "aggs": {
                                                    "related_words": {
                                                        "terms": {
                                                            "field": "search_word.keyword",
                                                            "size": 5,
                                                            "order": {"_count": "desc"},
                                                        }
                                                    }
                                                },
                                            }
                                        },
                                    }
                                },
                            }
                        },
                    }
                }
            },
        )

        # 既存のコード
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

        # 過去の検索ログを取得
        past_search_logs_response = client.search(
            index="past_search_log",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"user_id": 1}},
                        ]
                    }
                },
                "size": 5,
                "sort": {"created_at": {"order": "desc"}},
            },
        )

        past_search_logs = []
        for hit in past_search_logs_response["hits"]["hits"]:
            past_search_logs.append(hit["_source"])

        # 集計対象にするための検索ログを取得
        agg_past_search_logs_response = client.search(
            index="agg_past_search_log",
            body={
                "query": {"match": {"search_word": search_word}},
                "aggs": {
                    "agg_past_search_logs": {
                        "terms": {
                            "field": "related_search_word",
                            "size": 5,
                        }
                    }
                },
                "size": 5,
            },
        )

        agg_past_search_logs = []
        for hit in agg_past_search_logs_response["aggregations"][
            "agg_past_search_logs"
        ]["buckets"]:
            agg_past_search_logs.append(hit)

        # 関連の検索ワードを取得
        related_search_word_logs = []
        if client.count(index="related_search_word_log")["count"] > 0:
            related_search_word_response = client.search(
                index="related_search_word_log",
                body={
                    "query": {"match_phrase": {"search_query": search_word}},
                    "size": 5,
                    "sort": {"count": {"order": "desc"}},
                },
            )

            for hit in related_search_word_response["hits"]["hits"]:
                related_search_word_logs.append(hit["_source"]["related_search_word"])

        # ワードの順番を考慮しない、関連の検索ワードを取得
        no_order_related_search_word_logs = []

        if client.count(index="no_order_related_search_word_log")["count"] > 0:
            no_order_related_search_word_response = client.search(
                index="no_order_related_search_word_log",
                body={"query": {"match_phrase": {"search_query": search_word}}},
            )

            for hit in no_order_related_search_word_response["hits"]["hits"]:
                no_order_related_search_word_logs.append(
                    hit["_source"]["related_search_word"]
                )

        # タイトルのキーワードで集計
        title_aggression_response = client.search(
            index="blog",
            body={
                "query": {"match": {"title_aggression": search_word}},
                "aggs": {
                    "hoge_keywords": {
                        "terms": {
                            "field": "title_aggression",
                            "size": 5,
                        }
                    }
                },
            },
        )

        title_aggression_keywords = []
        for hit in title_aggression_response["aggregations"]["hoge_keywords"][
            "buckets"
        ]:
            title_aggression_keywords.append(hit["key"])

        # 過去履歴を集計
        past_search_logs_response = client.search(
            index="past_search_log",
            body={
                "query": {
                    "match": {
                        "search_word.standard": {
                            "query": search_word,
                        }
                    }
                },
                "aggs": {
                    "past_search_logs": {
                        "terms": {
                            "field": "search_word",
                            "size": 5,
                        }
                    }
                },
            },
        )

        past_search_aggregated_logs = []
        for hit in past_search_logs_response["aggregations"]["past_search_logs"][
            "buckets"
        ]:
            past_search_aggregated_logs.append(hit["key"])

        # 同じ時間帯の検索ワードの結果を処理
        time_based_results = []
        if "aggregations" in time_based_search_response:
            for timestamp_bucket in time_based_search_response["aggregations"][
                "search_times"
            ]["timestamps"]["buckets"]:
                timestamp = timestamp_bucket["key"]
                for related_bucket in timestamp_bucket["related_searches"][
                    "same_time_searches"
                ]["related_words"]["buckets"]:
                    time_based_results.append(
                        {
                            "timestamp": timestamp,
                            "word": related_bucket["key"],
                            "count": related_bucket["doc_count"],
                        }
                    )

        return (
            posts,
            suggestions,
            past_search_logs,
            agg_past_search_logs,
            related_search_word_logs,
            no_order_related_search_word_logs,
            title_aggression_keywords,
            past_search_aggregated_logs,
            time_based_results,
        )
