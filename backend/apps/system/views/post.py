from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Post
from ..serializers import PostSerializer, PaginationQuerySerializer, PostQuerySerializer, PostUpdateSerializer



class PostViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    update_body_serializer_class = PostUpdateSerializer
    update_body_id_field = 'post_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        s = PostQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        
        if data.get('postCode'):
            queryset = queryset.filter(post_code__icontains=data['postCode'])
        if data.get('postName'):
            queryset = queryset.filter(post_name__icontains=data['postName'])
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
            
        return queryset.order_by('post_sort')
