from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Source

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_type', 'status', 'items_extracted', 'uploaded_at', 'process_btn']
    list_filter = ['source_type', 'status', 'uploaded_at']
    search_fields = ['title', 'author', 'url']
    readonly_fields = ['uploaded_at', 'status', 'error_message']

    def items_extracted(self, obj):
        from core.models import Food
        return Food.objects.filter(source=obj).count()
    items_extracted.short_description = "Foods Extracted"

    def process_btn(self, obj):
        if obj.status in ('UPLOADED', 'FAILED', 'DONE'):
            url = reverse('documents:process', args=[obj.pk])
            if obj.status == 'UPLOADED':
                label = "▶ Process Now"
                style = "background:#2d6a4f; color:#fff; font-weight:700; padding:6px 12px; border-radius:6px; text-decoration:none; display:inline-block; box-shadow: 0 2px 6px rgba(45,106,79,0.3);"
            elif obj.status == 'DONE':
                label = "↺ Re-Process"
                style = "background:#52b788; color:#fff; font-weight:600; padding:4px 10px; border-radius:6px; text-decoration:none; display:inline-block;"
            else:
                label = "⚠ Retry Process"
                style = "background:#e76f51; color:#fff; font-weight:700; padding:6px 12px; border-radius:6px; text-decoration:none; display:inline-block;"

            return format_html(
                '<a class="button" style="{}" href="{}">{}</a>',
                style, url, label
            )
        return obj.status
    process_btn.short_description = "Actions"
