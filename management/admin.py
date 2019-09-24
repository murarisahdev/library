from django.contrib import admin

from .models import (Category, Author, BookCatalog,
	Review, ReadersTracker)


admin.site.register(Category)
admin.site.register(Author)
admin.site.register(BookCatalog)
admin.site.register(Review)
admin.site.register(ReadersTracker)