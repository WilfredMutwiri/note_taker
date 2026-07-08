from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source', 'verification', 'created_at')
    list_filter = ('source', 'verification')
    search_fields = ('title', 'subject', 'content')
