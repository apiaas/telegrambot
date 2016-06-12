from rest_framework import generics, status
from document.models import Document
from .serializers import DocumentSerializer, DocumentIndexSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_haystack.generics import HaystackGenericAPIView
import time
from drf_haystack.filters import HaystackHighlightFilter



class DocumentList(generics.ListCreateAPIView):
    """
    Document list.
    """
    permission_classes = (AllowAny,)
    model = Document
    serializer_class = DocumentSerializer

    # def post(self, request, *args, **kwargs):
    #     # up_file = request.FILES.get('file')
    #     data = request.data.copy()
    #     # data['filename'] = up_file.name
    #     # data['file'] = up_file
    #     # data['path'] = 'user_{0}/{1}_{2}'.format(request.user.id, str(time.time()), up_file.name)
    #     data['file_id'] = request.user.pk
    #     data['author'] = request.user.pk
    #     serializer = self.serializer_class(data=data)
    #     if serializer.is_valid():
    #         serializer.create(validated_data=serializer.validated_data, user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

document_list = DocumentList.as_view()


class DocumentDetail(generics.RetrieveUpdateAPIView):
    """
    Document detail.
    """

    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.all()

    def delete(self, request, pk, format=None):
        try:
            doc = Document.objects.get(pk=pk)
            doc.delete()
        except Document.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        return Response(status=status.HTTP_204_NO_CONTENT)

document_detail = DocumentDetail.as_view()


class DocumentSearchView(HaystackGenericAPIView):
    serializer_class = DocumentIndexSerializer
    index_models = [Document]
    # filter_backends = [HaystackHighlightFilter]

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(author=request.user.pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

document_search = DocumentSearchView.as_view()

