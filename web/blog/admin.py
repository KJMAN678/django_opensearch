from django.contrib import admin
from blog.models import Blog


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("title", "content")


admin.site.register(Blog, AuthorAdmin)
