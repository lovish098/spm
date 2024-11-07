from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import time, timedelta, datetime

# District model
class District(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# OPD types model
class OpdType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# AreaProfile model
class AreaProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uname = models.CharField(max_length=200, null=True, blank=True)
    uaddress = models.CharField(max_length=200, null=True, blank=True) 
    image = models.ImageField(upload_to='Area_img/', null=True, blank=True)     
    created = models.DateTimeField(auto_now_add=True)
    opd_types = models.ManyToManyField(OpdType, blank=True) 
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):
        return self.uname if self.uname else "Unnamed User" 

    class Meta:
        order_with_respect_to = 'user'

# UserProfile model
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_profile')
    uname = models.CharField(max_length=200, null=True, blank=True)
    umobile = models.CharField(max_length=200, null=True, blank=True)
    uemail = models.CharField(max_length=200, null=True, blank=True)
    uaddress = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='user_img/', null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    report = models.FileField(upload_to='user_reports/', null=True, blank=True)
    uaadhar = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    area_profile = models.ForeignKey(AreaProfile, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True) 
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uname if self.uname else "Unnamed User" 

    class Meta:
        order_with_respect_to = 'user'

# DoctorProfile model
class DoctorProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uname = models.CharField(max_length=200, null=True, blank=True)
    umobile = models.CharField(max_length=200, null=True, blank=True)
    uemail = models.CharField(max_length=200, null=True, blank=True)
    uaddress = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='user_img/', null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    uaadhar = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    opd_type = models.ForeignKey(OpdType, on_delete=models.CASCADE, null=True, blank=True) 
    area_profile = models.ForeignKey(AreaProfile, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)  

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uname if self.uname else "Unnamed User"  

    class Meta:
        order_with_respect_to = 'user'

# time slotes model

from django.db import models
from datetime import datetime, timedelta, time

class TimeSlot(models.Model):
    SESSION_CHOICES = [
        ('M', 'Morning'),
        ('E', 'Evening'),
    ]
    
    STATUS_CHOICES = [
        ('B', 'Booked'),
        ('C', 'Canceled'),
        ('A', 'Available'),
    ]

    session = models.CharField(max_length=1, choices=SESSION_CHOICES)
    time = models.TimeField() 
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A') 
    opd_type = models.ForeignKey(OpdType, on_delete=models.CASCADE, null=True, blank=True)  # Existing field
    area_profile = models.ForeignKey(AreaProfile, on_delete=models.CASCADE, null=True, blank=True)  # New field

    def __str__(self):
        opd_type_display = self.opd_type.name if self.opd_type else "No OPD Type"
        area_profile_display = self.area_profile.uname if self.area_profile else "No Area Profile"
        return f"{opd_type_display} - {area_profile_display} - {self.get_status_display()} - {self.get_session_display()} - {self.time.strftime('%H:%M')}"

    @staticmethod
    def generate_time_slots():
        """Generate time slots for Morning and Evening Sessions."""
        time_slots = []

        # Example OPD types (you can customize this as needed)
        opd_types = OpdType.objects.all()  # Fetch all OPD types
        area_profiles = AreaProfile.objects.all()  # Fetch all Area Profiles
        
        # Morning session: 09:00 to 12:00 (42 slots at 5-minute intervals)
        start_time = time(9, 0)
        total_slots_morning = 42
        for opd_type in opd_types:
            for area_profile in area_profiles:
                for _ in range(total_slots_morning):
                    time_slots.append((opd_type, 'M', start_time, area_profile))
                    start_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=5)).time()
                start_time = time(9, 0)  # Reset start time for the next OPD type

        # Evening session: 13:00 to 17:00 (48 slots at 5-minute intervals)
        start_time = time(13, 0)
        total_slots_evening = 48
        for opd_type in opd_types:
            for area_profile in area_profiles:
                for _ in range(total_slots_evening):
                    time_slots.append((opd_type, 'E', start_time, area_profile))
                    start_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=5)).time()
                start_time = time(13, 0)  # Reset start time for the next OPD type

        # Create time slots in the database if they don't already exist
        for opd_type, session, time_slot, area_profile in time_slots:
            TimeSlot.objects.get_or_create(session=session, time=time_slot, opd_type=opd_type, area_profile=area_profile)

    @staticmethod
    def get_available_slots(session, opd_type=None, area_profile=None):
        """Get available time slots, optionally filtered by OPD type and area profile."""
        filters = {'session': session, 'status': 'A'}
        if opd_type:
            filters['opd_type'] = opd_type
        if area_profile:
            filters['area_profile'] = area_profile
        return TimeSlot.objects.filter(**filters)


# class TimeSlot(models.Model):
#     SESSION_CHOICES = [
#         ('M', 'Morning'),
#         ('E', 'Evening'),
#     ]
    
#     STATUS_CHOICES = [
#         ('B', 'Booked'),
#         ('C', 'Canceled'),
#         ('A', 'Available'),
#     ]

#     session = models.CharField(max_length=1, choices=SESSION_CHOICES)
#     time = models.TimeField() 
#     status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A') 
#     opd_type = models.ForeignKey(OpdType, on_delete=models.CASCADE, null=True, blank=True)  # New field

#     def __str__(self):
#         # return f"{self.get_session_display()} - {self.time.strftime('%H:%M')} ({self.get_status_display()})"
#         # return f"{self.get_session_display()} - {self.time.strftime('%H:%M')}"
#         opd_type_display = self.opd_type.name if self.opd_type else "No OPD Type"
#         return f" {opd_type_display} - {self.get_status_display()} - {self.get_session_display()} - {self.time.strftime('%H:%M')}"

#     @staticmethod
#     def generate_time_slots():
#         """Generate time slots for Morning and Evening Sessions."""
#         time_slots = []

#         # Example OPD types (you can customize this as needed)
#         opd_types = OpdType.objects.all()  # Fetch all OPD types
        
#         # Morning session: 09:00 to 12:00 (42 slots at 5-minute intervals)
#         start_time = time(9, 0)
#         total_slots_morning = 42
#         for opd_type in opd_types:
#             for _ in range(total_slots_morning):
#                 time_slots.append((opd_type, 'M', start_time))
#                 start_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=5)).time()
#             start_time = time(9, 0)  # Reset start time for the next OPD type

#         # Evening session: 13:00 to 17:00 (48 slots at 5-minute intervals)
#         start_time = time(13, 0)
#         total_slots_evening = 48
#         for opd_type in opd_types:
#             for _ in range(total_slots_evening):
#                 time_slots.append((opd_type, 'E', start_time))
#                 start_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=5)).time()
#             start_time = time(13, 0)  # Reset start time for the next OPD type

#         # Create time slots in the database if they don't already exist
#         for opd_type, session, time_slot in time_slots:
#             TimeSlot.objects.get_or_create(session=session, time=time_slot, opd_type=opd_type)

#     @staticmethod
#     def get_available_slots(session, opd_type=None):
#         """Get available time slots, optionally filtered by OPD type."""
#         if opd_type:
#             return TimeSlot.objects.filter(session=session, status='A', opd_type=opd_type)
#         return TimeSlot.objects.filter(session=session, status='A')


class Appointment(models.Model):
    # Appointment Status Choices
    APPOINTMENT_STATUS = [
        ('B', 'Booked'),
        ('C', 'Canceled'),
        ('A', 'Available'),
    ]

    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    area_profile = models.ForeignKey(AreaProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Foreign keys linking to other models
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=True, blank=True)
    opd_type = models.ForeignKey('OpdType', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Appointment-specific fields
    appointment_status = models.CharField(max_length=1, choices=APPOINTMENT_STATUS, default='B')
    appointment_id = models.CharField(max_length=5, unique=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True)  
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            self.appointment_id = str(uuid.uuid4())[:5] 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.get_appointment_status_display()}"