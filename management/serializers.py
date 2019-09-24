from rest_framework import serializers

from .models import (Category, Author, BookCatalog,
    Review, ReadersTracker)


class AuthorSerializer(serializers.ModelSerializer):
    __doc__ = """Author serializer"""

    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = '__all__'

    def get_book_count(self, instance):
        return instance.books.all().count()


class CategorySerializer(serializers.ModelSerializer):
    __doc__ = """Category serializer"""

    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_book_count(self, instance):
        return instance.books.all().count()


class ReviewSerializer(serializers.ModelSerializer):
    __doc__ = """Review serializer"""

    book_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'book', 'reader', 'review', 'book_name')

    def get_book_name(self, instance):
        return instance.book.name


class PostReadersTrackerSerializer(serializers.ModelSerializer):
    __doc__ = """create Readers Tracker serializer"""

    class Meta:
        model = ReadersTracker
        fields = ('book', 'reader', 'percent')

    def create(self, validated_data):
        tracker, created = ReadersTracker.objects.get_or_create(
            book=validated_data['book'],
            reader=validated_data['reader'])

        if not created and int(validated_data['percent']) > tracker.percent:
            tracker.percent = validated_data['percent']
            tracker.save()

        return tracker


class GetBookCatalogSerializer(serializers.ModelSerializer):
    __doc__ = 'Book Catalog serializer'

    author = AuthorSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = BookCatalog
        fields = ('id', 'category', 'author',
            'name', 'book_cover', 'description',
            'reviews', 'file', 'can_review', 'created', 'updated')

    def get_can_review(self, instance):
        try:
            user = self.context['request'].user
        except:
            return False

        try:
            tracker = ReadersTracker.objects.get(
                book__id=instance.id,
                reader__id=user.id)

        except ReadersTracker.DoesNotExist:
            return False

        if(tracker.percent == 100):
            is_review = Review.objects.filter(
                book__id=instance.id,
                reader__id=user.id).exists()

            if not is_review:
                return True
        return False


class PostBookCatalogSerializer(serializers.ModelSerializer):
    __doc__ = 'Create Book Serializer'

    author = serializers.PrimaryKeyRelatedField(many=True, read_only=False,
        queryset=Author.objects.all(), required=False)

    class Meta:
        model = BookCatalog
        fields = ('category', 'author', 'name',
            'book_cover', 'description', 'file')


class GetReadersTrackerSerializer(serializers.ModelSerializer):
    __doc__ = 'Reader tracker serializer'

    book = GetBookCatalogSerializer()
    # book = serializers.SerializerMethodField()

    class Meta:
        model = ReadersTracker
        fields = ('id', 'book', 'reader', 'created',
            'updated', 'percent')

    def get_book(self, instance):
        serializer = GetBookCatalogSerializer(instance.book, 
            context={'request':self.context['request']})
        return serializer.data