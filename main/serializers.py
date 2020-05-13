from rest_framework import serializers

from . import models

class FileSerializer(serializers.ModelSerializer):

    class Meta():
        model = models.tempModel
        fields = ['file']

class TranslationSerializer(serializers.ModelSerializer):

  class Meta():
    model = models.translation
    fields = ['speech']