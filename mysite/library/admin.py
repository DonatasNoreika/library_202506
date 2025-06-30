from django.contrib import admin
from .models import Author, Book, Genre, BookInstance, BookReview, Profile

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'display_books']

class BookInstanceInLine(admin.TabularInline):
    model = BookInstance
    extra = 0
    readonly_fields = ['uuid']
    can_delete = False
    fields = ['uuid', 'due_back', 'status']


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'display_genre', 'cover']
    inlines = [BookInstanceInLine]


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['book', 'uuid', 'due_back', 'reader', 'status']
    list_filter = ['book', 'due_back', 'status']
    search_fields = ['uuid', 'book__title']
    list_editable = ['due_back', 'reader', 'status']

    fieldsets = (
        ('General', {'fields': ('uuid', 'book')}),
        ('Availability', {'fields': ('status', 'reader', 'due_back')}),
    )

class BookReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'date_created', 'reviewer', 'content']

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Profile)
