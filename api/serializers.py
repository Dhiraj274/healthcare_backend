from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Patient, Doctor, PatientDoctorMapping
 
class RegisterSerializer(serializers.ModelSerializer):
    # Ask the user for password twice so they don't mistype
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True) 
    last_name = serializers.CharField(required=False, allow_blank=True) # Optional
    email = serializers.EmailField(required=True) # Ensure email is explicitly required

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')

    def validate_email(self, value):
        # Make sure no one else has this email
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value
    
    def validate(self, attrs):
        # Double-check the passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return attrs

    def create(self, validated_data):
        # Build a new user and hash their password
        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Customizing TokenObtainPairSerializer to include username and email in the response (optional)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user details to the response data
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data
    

class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'address', 'phone_number', 'email', 'medical_history',
            'emergency_contact_name', 'emergency_contact_phone',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def validate_email(self, value):
        """
        Check that the email is unique for new patients.
        For updates, allow the same email if it belongs to the current instance.
        """
        query = Patient.objects.filter(email=value) 

        if self.instance: # If updating
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("A patient with this email already exists.")
        return value
    
    def create(self, validated_data):
        # Tie this patient to the logged-in user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)



class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'specialization', 'license_number', 'office_address', 'office_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

    def validate_email(self, value):
        query = Doctor.objects.filter(email=value)
        if self.instance: # If updating
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value

    def validate_license_number(self, value):
        query = Doctor.objects.filter(license_number=value)
        if self.instance: # If updating
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("A doctor with this license number already exists.")
        return value
    



class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), source='patient', write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor', write_only=True
    )

    # Read-only fields to provide more context in responses
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'id', 'patient_id', 'doctor_id', 'patient_details', 'doctor_details',
            'assigned_by', 'assignment_date', 'notes'
        ]
        read_only_fields = ('id', 'assignment_date', 'assigned_by', 'patient_details', 'doctor_details')

    def validate(self, data):
        # Only let users assign their own patients
        request_user = self.context['request'].user
        patient = data.get('patient') 

        if patient and patient.created_by != request_user:
            raise serializers.ValidationError(
                {"patient_id": "You can only assign doctors to patients you manage."}
            )
        return data

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        try:
            mapping = PatientDoctorMapping.objects.create(**validated_data)
            return mapping
        except Exception as e:
            raise serializers.ValidationError(f"This patient is already assigned to this doctor. ({str(e)})")