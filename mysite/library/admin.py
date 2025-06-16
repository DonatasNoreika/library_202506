from django.contrib import admin
from .models import Author, Book, Genre, BookInstance

class BookInstanceInLine(admin.TabularInline):
    model = BookInstance
    extra = 0
    readonly_fields = ['uuid']
    can_delete = False
    fields = ['uuid', 'due_back', 'status']


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'display_genre']
    inlines = [BookInstanceInLine]


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['book', 'uuid', 'due_back', 'status']
    list_filter = ['book', 'due_back', 'status']

    fieldsets = (
        ('General', {'fields': ('uuid', 'book')}),
        ('Availability', {'fields': ('status', 'due_back')}),
    )

# Register your models here.
admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
