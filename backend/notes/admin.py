from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source', 'created_at')
    list_filter = ('source',)
    search_fields = ('title', 'subject', 'content')
