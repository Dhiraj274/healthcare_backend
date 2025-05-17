from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    # Storing basic personal details for each patient
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # Patients might not always provide all contact details upfront,
    # so I made address and phone optional but keep email unique.
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)

    # A free-text field where clinicians can jot down any relevant
    # notes or background. Doesn’t have to be a formal history.
    medical_history = models.TextField(blank=True, null=True, help_text="Brief medical history")
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # Track who created this patient entry and when
    created_by = models.ForeignKey(User, related_name='patients_created', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # this Makes patient instances readable in admin and logs
        return f"{self.first_name} {self.last_name}"

    class Meta:
        # I want the newest entries up top, so this ordering makes that happen
        ordering = ['-created_at']



class Doctor(models.Model):
    # Core profile data for a doctor. We require email & license to be unique,
    # since those are primary identifiers in healthcare domain.
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True) # License should be unique

    # Office-specific info - not mandatory
    office_address = models.TextField(blank=True, null=True)
    office_hours = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"

    class Meta:
        # Sort alphabetically by last, then first name
        ordering = ['last_name', 'first_name']



class PatientDoctorMapping(models.Model):
    # Linking patients and doctors, with optional notes
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doctor_mappings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_mappings')
    
    # Whomever makes the assignment gets recorded here.
    # Using SET_NULL in case that user account is deleted later.
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_mappings')
    assignment_date = models.DateTimeField(auto_now_add=True)
    
    # Optional notes on why this doctor was chosen or any special instructions
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about the assignment")

    class Meta:
        # this will prevent duplicate assignments of the same patient-doctor pair
        unique_together = ('patient', 'doctor')
        ordering = ['-assignment_date']

    def __str__(self):
        return f"{self.patient} assigned to {self.doctor}"