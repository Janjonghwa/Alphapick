from rest_framework import permissions, viewsets

from .models import WorkoutRecord
from .serializers import WorkoutRecordSerializer


class WorkoutRecordViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutRecord.objects.select_related("course__category").filter(user=self.request.user)
