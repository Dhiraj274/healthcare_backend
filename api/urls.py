from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import ( 
    RegisterView,
    PatientViewSet,
    DoctorViewSet,
    PatientDoctorMappingViewSet,
    PatientAssignmentsView
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'mappings', PatientDoctorMappingViewSet, basename='mapping')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('mappings/by-patient/<int:patient_id>/', PatientAssignmentsView.as_view(), name='patient_assignments_list'), # Custom route
    path('', include(router.urls)),
]