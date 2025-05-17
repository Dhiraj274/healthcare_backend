from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status, serializers, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, PatientSerializer, DoctorSerializer, PatientDoctorMappingSerializer
from .models import Patient, Doctor, PatientDoctorMapping
from rest_framework.decorators import action

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # Anyone can register
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "message": "User registered successfully. Please log in."
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the creator of the patient.
        return obj.created_by == request.user

class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly] # Ensure user is authenticated and is owner for write ops

    def get_queryset(self):
        """
        This view should return a list of all the patients
        created by the currently authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            return Patient.objects.filter(created_by=user)
        return Patient.objects.none() 

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all() 
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]



class PatientDoctorMappingViewSet(viewsets.ModelViewSet):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all mappings
        where the patient was created by the currently authenticated user.
        Or, if the user is an admin/superuser, show all.
        """
        user = self.request.user
        if user.is_superuser: # Admins can see all mappings
            return PatientDoctorMapping.objects.all()
        # Regular users see mappings related to patients they manage
        return PatientDoctorMapping.objects.filter(patient__created_by=user)

    def perform_create(self, serializer):
        serializer.save()


    def get_object(self):
        """
        Override get_object to ensure user has permission for the specific mapping instance.
        This is for retrieve, update, destroy actions on /api/mappings/{mapping_id}/.
        """
        obj = super().get_object()
        user = self.request.user
        if not user.is_superuser and obj.patient.created_by != user:
            self.permission_denied(
                self.request, message="You do not have permission to access this mapping."
            )
        return obj

class PatientAssignmentsView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        patient_id = self.kwargs.get('patient_id')
        try:
            # Ensure the patient exists and belongs to the user (or user is admin)
            patient = Patient.objects.get(id=patient_id)
            if not user.is_superuser and patient.created_by != user:
                return Doctor.objects.none()

            return Doctor.objects.filter(patient_mappings__patient_id=patient_id).distinct()

        except Patient.DoesNotExist:
            return Doctor.objects.none()
