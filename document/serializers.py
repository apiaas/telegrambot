from rest_framework import serializers
from guardian.shortcuts import assign_perm
from document.models import Document
from document.search_indexes import DocumentIndex
from django.db import transaction
from drf_haystack.serializers import HaystackSerializer


class DocumentSerializer(serializers.ModelSerializer):

    def create(self, validated_data, user):
        with transaction.atomic():
            obj = super(DocumentSerializer, self).create(validated_data)
            # assign_perm(Document.CAN_VIEW, user, obj)
            # assign_perm(Document.CAN_DELETE, user, obj)
            # assign_perm(Document.CAN_UPDATE, user, obj)
            return obj

    class Meta:
        model = Document
        # extra_kwargs = {'path': {'write_only': True}, 'filename': {'write_only': True}}


class DocumentIndexSerializer(HaystackSerializer):

    class Meta:
        model = Document
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [DocumentIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
            "text", "description", "processed_text", 'path', 'author',
        ]
