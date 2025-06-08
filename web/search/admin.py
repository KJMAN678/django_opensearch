from django.contrib import admin
from search.models import SearchLog


class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("user_id", "search_query", "searched_at")


admin.site.register(SearchLog, SearchLogAdmin)
