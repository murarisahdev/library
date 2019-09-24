from django.db import models
from django.contrib.auth.models import User


class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    __doc__ = "Book Categories"

    name = models.CharField(max_length=100)

    def __str__(self):
        return '{0}'.format(self.name)


class Author(models.Model):
    __doc__ = "Book Author"

    name = models.CharField(max_length=100)

    def __str__(self):
        return '{0}'.format(self.name)


def book_cover_path(instance, filename):
    splitted = filename.split('.')
    extension = splitted[1]
    return 'book_cover/{0}_{1}.{2}'.format(
        instance.id, splitted[0], extension)


def book_file_path(instance, filename):
    splitted = filename.split('.')
    extension = splitted[1]
    return 'book_file/{1}.{2}'.format(
        instance.id, splitted[0], extension)


class BookCatalog(TimeStampModel):
    __doc__ = "Book Catalog"

    name = models.CharField(max_length=100)
    book_cover = models.ImageField(
        blank=False,
        upload_to=book_cover_path,
        default='../default/default_cover.png')
    description = models.TextField(default='')
    category = models.ForeignKey(Category,
        on_delete=models.CASCADE,
        related_name='books')
    author = models.ManyToManyField(Author,
        related_name='books')
    file = models.FileField(
        default='../default/nobook.pdf',
        blank=False,
        upload_to=book_file_path,)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return '{}'.format(self.name)
    

class Review(TimeStampModel):
    __doc__ = "Book Reviews"

    book = models.ForeignKey(BookCatalog,
        on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=100)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return 'Book: {0} - {1}'.format(self.book.name, self.review)


class ReadersTracker(TimeStampModel):
    __doc__ = "Book Reader Track"

    book = models.ForeignKey(BookCatalog,
        on_delete=models.CASCADE, related_name='readerstraker')
    reader = models.ForeignKey(User,
        on_delete=models.CASCADE, related_name='readerstraker')
    percent = models.IntegerField(default=0)

    def __str__(self):
        return 'Book: {0} - {1}'.format(
            self.reader.username, self.book.name)
