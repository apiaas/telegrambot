from rest_framework import serializers
from document.models import Document
from document.search_indexes import DocumentIndex
from django.db import transaction
from drf_haystack.serializers import HaystackSerializer, HighlighterMixin


class DocumentSerializer(serializers.ModelSerializer):

    def create(self, validated_data, user):
        with transaction.atomic():
            obj = super(DocumentSerializer, self).create(validated_data)
            return obj

    class Meta:
        model = Document


class DocumentIndexSerializer(HighlighterMixin, HaystackSerializer):

    highlighter_css_class = None
    highlighter_html_tag = "b"
    highlighter_field = "processed_text"

    class Meta:
        model = Document
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [DocumentIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
            "text", "processed_text", "author", "file_id"
        ]
