from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Box, Order, Product
from .serializers import (
    BoxSerializer,
    OrderSerializer,
    ProductSerializer,
    RecommendRequestSerializer,
    recommendation_to_dict,
)
from .services import RecommendationError, recommend_box, recommend_for_order


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related("items__product").select_related("recommended_box")
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"], url_path="recommend-box")
    def recommend_box(self, request, pk=None):
        """Compute the best box for a saved order and store it on the order."""
        order = self.get_object()
        try:
            rec = recommend_for_order(order)
        except RecommendationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(recommendation_to_dict(rec))


@api_view(["POST"])
def recommend(request):
    """Recommend a box for a list of items without creating an order."""
    serializer = RecommendRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    lines = [(i["product"], i["quantity"]) for i in serializer.validated_data["items"]]
    try:
        rec = recommend_box(lines)
    except RecommendationError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(recommendation_to_dict(rec))
