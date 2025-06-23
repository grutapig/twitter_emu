from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Community, Tweet


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'screen_name', 'twitter_id', 'email', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('^username', 'twitter_id')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Twitter Profile', {
            'fields': ('name', 'screen_name', 'followers', 'twitter_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('followers',)


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('twitter_id', 'name', 'created_at', 'updated_at')
    search_fields = ('name', 'twitter_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('id', 'twitter_id', 'author', 'community', 'text_preview', 'reply_to_display', 'updated_at', 'created_at')
    list_filter = ('created_at', 'community', 'author')
    search_fields = ('^text', '=author__screen_name', 'community__name', 'twitter_id')
    ordering = ('-id',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('reply_to', 'author')
    autocomplete_fields = ('community',)
    list_per_page = 50
    list_max_show_all = 200

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    def reply_to_display(self, obj):
        if obj.reply_to:
            return f"Reply to: {obj.reply_to.twitter_id} (@{obj.reply_to.author.screen_name})"
        return "Original Tweet"

    text_preview.short_description = 'Text Preview'
    reply_to_display.short_description = 'Reply Status'
