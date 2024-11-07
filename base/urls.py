from django.urls import path 
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from . import views

# from . import views - > views.viewname.as_view()


urlpatterns = [

    #authentication and registration

    #normal user
    path('ulogin/',BaseUserLogin.as_view(),name='ulogin'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('uregister/',BaseUserRegister.as_view(),name='uregister'),

    path('uprofile/',BaseUserProfile.as_view(),name='uprofile'),
    path('uuprofile/<str:uname>/', BaseUserUpdateProfile.as_view(), name='uuprofile'),

    #appointment download
     path('dappointment/', DownloadAppointmentPDF.as_view(), name='dappointment'),

    #doctor user
    path('dlogin/',BaseDoctorLogin.as_view(),name='dlogin'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dregister/',BaseDoctorRegister.as_view(),name='dregister'),

    path('dprofile/',BaseDoctorProfile.as_view(),name='dprofile'),
    path('duprofile/<str:uname>/', BaseDoctorUpdateProfile.as_view(), name='duprofile'),
    path('ddashboard/',BaseDoctorDashboard.as_view(),name='ddashboard'),
    path('cancel_appointment/<int:pk>/', CancelAppointmentView.as_view(), name='cancel_appointment'),
    path('patient_profile/<int:pk>/', PatientProfileView.as_view(), name='patient_profile'),
    path('download-appointments/', AppointmentDownloadView.as_view(), name='download_appointments'),

    #area user
    path('rlogin/',BaseRegionalLogin.as_view(),name='rlogin'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('rregister/',BaseRegionalRegister.as_view(),name='rregister'),

    path('rprofile/',BaseAreaProfile.as_view(),name='rprofile'),
    path('ruprofile/<str:uname>/', BaseAreaUpdateProfile.as_view(), name='ruprofile'),
    path('rdashboard/',BaseAreaDashboard.as_view(),name='rdashboard'),
    path('rpatient_profile/<int:pk>/', RegionalPatientProfileView.as_view(), name='rpatient_profile'),
    path('rdoctor_profile/<int:pk>/', RegionalDoctorProfileView.as_view(), name='rdoctor_profile'),
    path('download-area-user/', AreaUserDownloadView.as_view(), name='download-area-user'),

  

    #appointment
    path('appointment/',BaseAppointment.as_view(),name='appointment'),
    

    #nav bar urls
    path('',BaseHome.as_view(),name='home'),
    path('home/',BaseHome.as_view(),name='home'),
    path('aboutus/',BaseAboutus.as_view(),name='aboutus'),
    path('help/',BaseHelp.as_view(),name='help'),
    path('contactus/',BaseContactUs.as_view(),name='contactus'),

    #time slotes 
    path('get_available_slots/<str:session>/', views.get_available_slots, name='get_available_slots'),

    

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
