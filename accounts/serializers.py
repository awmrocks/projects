from rest_framework import serializers
from .models import StudentProfile

class StudentVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id_card_image', 'is_verified']