from django.contrib import admin
from .models import UserProfile , DoctorProfile , AreaProfile , OpdType , District , Appointment , TimeSlot

# from import_export.admin import ImportExportModelAdmin
# export import data from django-import-export module


admin.site.register(UserProfile)
admin.site.register(DoctorProfile)
admin.site.register(AreaProfile)
admin.site.register(OpdType)
admin.site.register(District)
admin.site.register(Appointment)
admin.site.register(TimeSlot)