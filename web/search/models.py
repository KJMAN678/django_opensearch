from django.db import models


class SearchLog(models.Model):
    user_id = models.CharField(max_length=255)
    search_query = models.CharField(max_length=255)
    searched_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "search_log"
