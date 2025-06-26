from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_rating = self.request.query_params.get('min_rating')
        min_reviews = self.request.query_params.get('min_reviews')

        if min_price:
            queryset = queryset.filter(discounted_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(discounted_price__lte=max_price)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if min_reviews:
            queryset = queryset.filter(review_count__gte=min_reviews)
        return queryset
