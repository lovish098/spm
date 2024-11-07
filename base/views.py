# importing basic modules
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views.generic import TemplateView  
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import RedirectView
from django.views import View
from django.contrib import messages
from django import forms
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse
from django.conf.urls import handler404
 
#pdf / excel sheet / csv usage releated modules
import os 
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import pandas as pd
import csv


# import essential modules for auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


#import models.py
from base.models import *


# -----------------------------------------------------------------------------------------------------



class RegionalDoctorProfileView(LoginRequiredMixin, DetailView):
    model = DoctorProfile
    template_name = 'dashboard/rdoctor_profile.html'
    context_object_name = 'doctor_profile'

    def get_object(self):
        # Get the doctor's profile based on the URL parameter (primary key)
        return DoctorProfile.objects.get(pk=self.kwargs['pk'])


# -----------------------------------------------------------------------------------------------------

class RegionalPatientProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'dashboard/rpatient_profile.html'
    context_object_name = 'patient_profile'

    def get_object(self):
        # Get the patient's profile based on the URL parameter (primary key)
        return UserProfile.objects.get(pk=self.kwargs['pk'])


# -----------------------------------------------------------------------------------------------------

# dash board for area /regional

class BaseAreaDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/rdashboard.html'
    model = AreaProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the area profile for the logged-in user
        area_profile = AreaProfile.objects.filter(user=self.request.user).first()

        # Filter doctor profiles and user profiles based on the current user's area profile
        doctor_profiles = DoctorProfile.objects.filter(area_profile=area_profile)
        user_profiles = UserProfile.objects.filter(area_profile=area_profile)

        # Add to context
        context['area_profile'] = area_profile
        context['doctor_profile'] = doctor_profiles
        context['user_profile'] = user_profiles

        return context


class AreaUserDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get the area profile for the logged-in user
        area_profile = AreaProfile.objects.filter(user=request.user).first()

        # Get parameters from request
        user_type = request.GET.get('user_type')
        format = request.GET.get('format', 'csv')  # Default to CSV if not specified

        # Filter based on the user_type parameter
        if user_type == 'patient':
            user_profiles = UserProfile.objects.filter(area_profile=area_profile)
            doctor_profiles = []
        elif user_type == 'doctor':
            user_profiles = []
            doctor_profiles = DoctorProfile.objects.filter(area_profile=area_profile)
        else:
            return HttpResponse('Invalid user type', status=400)

        # Determine format and call appropriate download function
        if format == 'csv':
            return self.download_csv(user_profiles, doctor_profiles)
        elif format == 'xls':
            return self.download_xls(user_profiles, doctor_profiles)

        return HttpResponse('Invalid format', status=400)

    def download_csv(self, user_profiles, doctor_profiles):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="area_users.csv"'

        writer = csv.writer(response)
        writer.writerow(['Type', 'User ID', 'Username', 'Email'])  # Header row

        # Write user profiles
        for user in user_profiles:
            writer.writerow(['User', user.id, user.uname, user.uemail])

        # Write doctor profiles
        for doctor in doctor_profiles:
            writer.writerow(['Doctor', doctor.id, doctor.uname, doctor.uemail])

        return response

    def download_xls(self, user_profiles, doctor_profiles):
        # Prepare data for user profiles or doctor profiles only, based on user_type
        data = {
            'Type': ['User'] * len(user_profiles) + ['Doctor'] * len(doctor_profiles),
            'User ID': [user.id for user in user_profiles] + [doctor.id for doctor in doctor_profiles],
            'Username': [user.uname for user in user_profiles] + [doctor.uname for doctor in doctor_profiles],
            'Email': [user.uemail for user in user_profiles] + [doctor.uemail for doctor in doctor_profiles],
        }

        df = pd.DataFrame(data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="area_users.xlsx"'

        # Write the DataFrame to the response using openpyxl
        df.to_excel(response, index=False)

        return response

# -----------------------------------------------------------------------------------------------------
#update / add basic details of area
class AreaProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['uname','uaddress','image','opd_type','district']


class BaseAreaUpdateProfile(LoginRequiredMixin,UpdateView):
    template_name = "profile/ruprofile.html"
    model = AreaProfile
    form_class = AreaProfileForm  
    success_url = reverse_lazy('rprofile') 

    def get_queryset(self):
        return AreaProfile.objects.all()

    def get_object(self, queryset=None):
        username = self.kwargs.get('uname')
        return get_object_or_404(AreaProfile, uname=username)

    def get_initial(self):
        initial = super().get_initial()
        area_profile = self.get_object()
        initial['uname'] = area_profile.uname
        initial['uaddress'] = area_profile.uaddress
        initial['image'] = area_profile.image
        # Set the initially selected opd_types
        initial['opd_types'] = area_profile.opd_types.all()  
        initial['district'] = area_profile.district
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the available OPD types to the context
        context['opd_types'] = OpdType.objects.all()  # Fetch all OPD types
        return context


#Area  profile page
class BaseAreaProfile(LoginRequiredMixin,DetailView):
    model = AreaProfile
    template_name = "profile/regionalprofile.html"
    context_object_name = 'area_profile'

    def get_object(self, queryset=None):
        return AreaProfile.objects.filter(user=self.request.user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opd_types'] = OpdType.objects.all()  
        return context    


# -----------------------------------------------------------------------------------------------------

class BaseDoctorDashboard(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'dashboard/ddashboard.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        # Return all appointments without filtering here
        return Appointment.objects.all()

    def get_context_data(self, **kwargs):
        # Add the doctor profile to the context
        context = super().get_context_data(**kwargs)
        doctor_profile = DoctorProfile.objects.get(user=self.request.user)
        context['doctor_profile'] = doctor_profile
        
        # Fetch appointments based on doctor's OPD type
        appointments = Appointment.objects.filter(opd_type=doctor_profile.opd_type).select_related('user_profile', 'time_slot')

        # Optional: Filter by area profile if needed
        # if doctor_profile.area_profile:
        #     appointments = appointments.filter(user_profile__area_profile=doctor_profile.area_profile)

        # Optional: Filter by district if needed
        # if doctor_profile.district:
        #     appointments = appointments.filter(user_profile__district=doctor_profile.district)

        context['appointments'] = appointments
        return context



class AppointmentDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        format = request.GET.get('format')
        doctor_profile = DoctorProfile.objects.get(user=request.user)

        # Fetch appointments based on doctor's OPD type
        appointments = Appointment.objects.filter(opd_type=doctor_profile.opd_type).select_related('user_profile', 'time_slot')

        if format == 'csv':
            return self.download_csv(appointments)
        elif format == 'xls':
            return self.download_xls(appointments)

        return HttpResponse('Invalid format', status=400)

    def download_csv(self, appointments):
        # Create a CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="appointments.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Appointment ID', 'User ', 'Date', 'Status', 'Time Slot'])  # Header row
        
        for appointment in appointments:
            writer.writerow([
                appointment.appointment_id,
                appointment.user_profile.uname,
                appointment.created.strftime('%Y-%m-%d %H:%M:%S'),
                appointment.appointment_status,
                appointment.time_slot.time.strftime('%H:%M') if appointment.time_slot else 'N/A'
            ])
        return response

    def download_xls(self, appointments):
        # Create a DataFrame and then an Excel response
        data = {
            'Appointment ID': [appointment.appointment_id for appointment in appointments],
            'User ': [appointment.user_profile.uname for appointment in appointments],
            'Date': [appointment.created.strftime('%Y-%m-%d %H:%M:%S') for appointment in appointments],
            'Status': [appointment.appointment_status for appointment in appointments],
            'Time Slot': [appointment.time_slot.time.strftime('%H:%M') if appointment.time_slot else 'N/A' for appointment in appointments],
        }
        
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="appointments.xlsx"'
        
        # Use pandas to write the DataFrame to the response
        df.to_excel(response, index=False)
        return response



# ---------------------------------------------------------------------------------------

class PatientProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'dashboard/patient_profile.html'
    context_object_name = 'patient_profile'

    def get_object(self):
        # Get the patient's profile based on the URL parameter (primary key)
        return UserProfile.objects.get(pk=self.kwargs['pk'])


class CancelAppointmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
      
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Check if the logged-in user is the doctor of this appointment's OPD type
        doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
        if appointment.opd_type != doctor_profile.opd_type:
            messages.error(request, "You are not authorized to cancel this appointment.")
            return redirect(reverse('doctor_dashboard'))

        # Mark the appointment as canceled
        appointment.appointment_status = 'C'

        if appointment.time_slot:
            appointment.time_slot.status = 'A'  # Assuming 'A' stands for Available
            appointment.time_slot.save()   

        appointment.save()

       
        appointment.delete()

        # Construct the file path for the appointment PDF
        pdf_filename = f"{appointment.appointment_id}_appointment.pdf"
        print(pdf_filename)  
        pdf_file_path =  os.path.join(settings.BASE_DIR, "media", 'appointment',  pdf_filename)

        # Delete the PDF file if it exists
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path) 



        # Send email notification if user's email is available
        if appointment.user_profile.uemail:
            subject = "Appointment Booking Notification"
            message = (
                f"Dear {appointment.user_profile.uname},\n\n"
                f"Your appointment (ID: {appointment.appointment_id}) has been canceled due to doctor meetings.\n"
                f"Time Slot: {appointment.time_slot}\n\n"
                "Thank you!"
            )
            recipient_list = [appointment.user_profile.uemail]
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Sender email from settings
                    recipient_list,
                    fail_silently=False
                )
                messages.success(request, "Appointment cancel by doctor  and email notification sent.")
            except Exception as e:
                messages.error(request, f"Appointment canceled, but an error occurred while sending email: {e}")

        messages.success(request, "The appointment has been canceled and the patient has been notified.")
        return redirect('ddashboard')

# -----------------------------------------------------------------------------------------------------


def get_available_slots(request, session):
    # Validate session input
    if session not in ['M', 'E']:  # Assuming 'M' for Morning and 'E' for Evening
        return JsonResponse({'error': 'Invalid session type'}, status=400)

    # Query available slots (pending slots) for the given session
    available_slots = TimeSlot.objects.filter(session=session, status='P')  # Changed to 'P' for Pending
    
    # Prepare the data to send as JSON
    slots_data = []
    for slot in available_slots:
        slots_data.append({
            'id': slot.id,
            'time': slot.time.strftime('%H:%M'),  # Format time as 'HH:MM'
            'status': slot.get_status_display(),
            'session': slot.get_session_display()  # Get human-readable session
        })
    
    # Return the JSON response
    return JsonResponse({'slots': slots_data})



# -----------------------------------------------------------------------------------------------------

def create_pdf(user_name, unique_id, age, mobile, opd_type):
    # Use Django's static method to get the logo path if it's in static files
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo.png")  

    # Create the output directory if it doesn't exist
    output_dir = os.path.join(settings.BASE_DIR, "media", 'appointment')
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Define the output PDF file path
    output_file_path = os.path.join(output_dir, f'{unique_id}_appointment.pdf')

    # Create a canvas
    c = canvas.Canvas(output_file_path, pagesize=letter)
    width, height = letter

    # Draw the logo on the left side
    try:
        logo_width = 2 * inch  # Set the width of the logo
        logo_height = 2 * inch  # Set the height of the logo
        c.drawImage(logo_path, 0.5 * inch, height - logo_height - 0.5 * inch, width=logo_width, height=logo_height)
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Set the position for the user details on the right side
    text_x = 4 * inch
    text_y = height - 1 * inch

    # Set font and color for the user details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)

    # Draw user details
    c.drawString(text_x, text_y - 0.2 * inch, f"Unique ID: {unique_id}")
    c.drawString(text_x, text_y - 0.6 * inch, f"OPD Type: {opd_type}")  
    c.drawString(text_x, text_y, f"Name: {user_name}")
    c.drawString(text_x, text_y - 0.4 * inch, f"Age: {age}")
    c.drawString(text_x, text_y - 0.8 * inch, f"Mobile No: {mobile}") 

    # Draw a dark black line below the user details
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.line(text_x - 0.5 * inch, text_y - 0.9 * inch, width - 0.5 * inch, text_y - 0.9 * inch)  # Adjusted line position

    # Save the PDF
    c.save()

    return output_file_path

class BaseAppointment(LoginRequiredMixin,TemplateView):
    model = UserProfile
    template_name = "appointment/bookappointment.html"
    context_object_name = 'user_profile'
    success_url = reverse_lazy('home') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the UserProfile for the logged-in user
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        context[self.context_object_name] = user_profile

        # Fetch the related AreaProfile
        # area_profile = AreaProfile.objects.filter(user=user_profile.user).first() if user_profile else None
        # context['area_profile'] = area_profile
        area_profile = AreaProfile.objects.all()
        context['area_profile'] = area_profile

        # Fetch all OPD types and pass them to the context
        context['opd_types'] = OpdType.objects.all()

        # Fetch all districts and pass them to the context
        context['district'] = District.objects.all()

        # Fetch available time slots
        morning_slots = TimeSlot.get_available_slots('M')  
        evening_slots = TimeSlot.get_available_slots('E') 

        context['morning_slots'] = morning_slots
        context['evening_slots'] = evening_slots

        return context

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.filter(user=self.request.user).first()

        # Get OPD type and time slot from POST request
        opd_type_id = request.POST.get('opd')  
        time_slot_id = request.POST.get('time_slot')
        district_id = request.POST.get('district')  
        area_profile_id = request.POST.get('area_profile')  

        if not user_profile:
            messages.error(request, "User profile not found.")
            return redirect('home')

        # Validate OPD type and time slot
        opd_type = OpdType.objects.filter(id=opd_type_id).first()
        time_slot = TimeSlot.objects.filter(id=time_slot_id, status='A').first() 
        district = District.objects.filter(id=district_id).first()
        area_profile = AreaProfile.objects.filter(id=area_profile_id).first() 

        if not opd_type:
            messages.error(request, "Invalid OPD type selected.")
            return redirect('home')

        if not time_slot:
            messages.error(request, "Selected time slot is not available.")
            return redirect('home')

        # Create a new appointment
        appointment = Appointment.objects.create(
            user_profile=user_profile,
            opd_type=opd_type,
            district = district,
            area_profile=area_profile,  
            appointment_status='B',  # B for booked
            time_slot=time_slot
        )

        # Mark the time slot as booked
        time_slot.status = 'B'
        time_slot.save()

        # Generate PDF
        pdf_file_path = create_pdf(
            user_name=user_profile.uname,
            unique_id=appointment.appointment_id,
            age=user_profile.age,
            mobile=user_profile.umobile,
            opd_type=opd_type,
        )



        # Send success message
        messages.success(request, "Appointment booked successfully.")
        
        # Send email notification if user's email is available
        if appointment.user_profile.uemail:
            subject = "Appointment Booking Notification"
            message = (
                f"Dear {appointment.user_profile.uname},\n\n"
                f"Your appointment (ID: {appointment.appointment_id}) has been successfully booked.\n"
                f"Time Slot: {appointment.time_slot}\n\n"
                "Thank you!"
            )
            recipient_list = [appointment.user_profile.uemail]
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Sender email from settings
                    recipient_list,
                    fail_silently=False
                )
                messages.success(request, "Appointment booked and email notification sent.")
            except Exception as e:
                messages.error(request, f"Appointment booked, but an error occurred while sending email: {e}")

        return redirect('home')



class DownloadAppointmentPDF(View):
    template_name = "appointment/downloadappointment.html"  # Ensure this template exists

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        unique_id = request.POST.get('unique_id')

        # Fetch the appointment based on the unique ID
        appointment = Appointment.objects.filter(appointment_id=unique_id).first()

        if not appointment:
            messages.error(request, "No appointment found with this ID.")
            return redirect('download_appointment_pdf')  # Redirect to the download page

        # Generate the PDF file
        pdf_file_path = create_pdf(
            user_name=appointment.user_profile.uname,
            unique_id=appointment.appointment_id,
            age=appointment.user_profile.age,
            mobile=appointment.user_profile.umobile,
            opd_type=appointment.opd_type,
        )

        # Check if the PDF file was created successfully
        if pdf_file_path is None:
            messages.error(request, "Failed to generate the PDF. Please try again.")
            return redirect('home')  # Redirect to the download page
 
        # Serve the PDF file for download
        try:
            with open(pdf_file_path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{appointment.appointment_id}_appointment.pdf"'
                return response
        except FileNotFoundError:
            messages.error(request, "The PDF file was not found. Please try again.")
            return redirect('home')  # Redirect to the download page
        except Exception as e:
            messages.error(request, f"An error occurred while trying to download the PDF: {e}")
            return redirect('home')





# -----------------------------------------------------------------------------------------------------

#Doctor  profile page
class BaseDoctorProfile(LoginRequiredMixin,DetailView):
    model = DoctorProfile
    template_name = "profile/doctorprofile.html"
    context_object_name = 'doctor_profile'

    def get_object(self, queryset=None):
        return DoctorProfile.objects.filter(user=self.request.user).first()
      
# -----------------------------------------------------------------------------------------------------
#update / add basic details of doctor
class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['uname', 'umobile', 'uemail', 'uaddress', 'gender', 'age', 'date_of_birth', 'uaadhar', 'image', 'area_profile','opd_type','district']

class BaseDoctorUpdateProfile(LoginRequiredMixin,UpdateView):
    template_name = "profile/duprofile.html"
    model = DoctorProfile
    form_class = DoctorProfileForm  
    success_url = reverse_lazy('dprofile') 

    def get_queryset(self):
        
        return DoctorProfile.objects.all()

    def get_object(self, queryset=None):
        
        username = self.kwargs.get('uname')
       
        return get_object_or_404(DoctorProfile, uname=username)

    def form_valid(self, form):
        
        if form.cleaned_data['gender'] == '':
            form.instance.gender = None  
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        doctor_profile = self.get_object()
        initial['uname'] = doctor_profile.uname
        initial['umobile'] = doctor_profile.umobile
        initial['uemail'] = doctor_profile.uemail
        initial['uaddress'] = doctor_profile.uaddress
        initial['gender'] = doctor_profile.gender
        initial['age'] = doctor_profile.age
        initial['date_of_birth'] =doctor_profile.date_of_birth
        initial['uaadhar'] = doctor_profile.uaadhar
        initial['image'] = doctor_profile.image
        initial['area_profile'] = doctor_profile.area_profile
        initial['opd_type'] = doctor_profile.opd_type
        initial['district'] = doctor_profile.district

        return initial


# -----------------------------------------------------------------------------------------------------
#update / add basic details of user
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['uname', 'umobile', 'uemail', 'uaddress', 'gender', 'age', 'date_of_birth', 'uaadhar', 'image', 'area_profile','district']

class BaseUserUpdateProfile(LoginRequiredMixin,UpdateView):
    template_name = "profile/uuprofile.html"
    model = UserProfile
    form_class = UserProfileForm  
    success_url = reverse_lazy('uprofile')  

    def get_queryset(self):
       
        return UserProfile.objects.all()

    def get_object(self, queryset=None):
      
        username = self.kwargs.get('uname')
       
        return get_object_or_404(UserProfile, uname=username)

    def form_valid(self, form):
       
        if form.cleaned_data['gender'] == '':
            form.instance.gender = None  
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        user_profile = self.get_object()
        initial['uname'] = user_profile.uname
        initial['umobile'] = user_profile.umobile
        initial['uemail'] = user_profile.uemail
        initial['uaddress'] = user_profile.uaddress
        initial['gender'] = user_profile.gender
        initial['age'] = user_profile.age
        initial['date_of_birth'] = user_profile.date_of_birth
        initial['uaadhar'] = user_profile.uaadhar
        initial['image'] = user_profile.image
        initial['area_profile'] = user_profile.area_profile
        initial['district'] = user_profile.district

        return initial
# -----------------------------------------------------------------------------------------------------

#user profile page
class BaseUserProfile(LoginRequiredMixin,DetailView):
    model = UserProfile
    template_name = "profile/userprofile.html"
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        return UserProfile.objects.filter(user=self.request.user).first()


# -----------------------------------------------------------------------------------------------------

#contact us  
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

class BaseContactUs(FormView):
    template_name = "base/contactus.html"
    form_class = ContactForm  
    success_url = reverse_lazy('contactus')  

    def form_valid(self, form):
        name = form.cleaned_data['name']
        mobile = form.cleaned_data['mobile']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        full_message = f"name : {name} \n email : {email} \n mobile : {mobile} \n\n message : {message}"

        send_mail(
            subject,
            full_message,
            email,
            ['sparsh.healthservice@gmail.com'], 
            fail_silently=False,
        )

        messages.success(self.request, "Message sent successfully.")
        return super().form_valid(form)
   
# -----------------------------------------------------------------------------------------------------

#help us 
class BaseHelp(TemplateView):
    template_name = "base/help.html"

# -----------------------------------------------------------------------------------------------------

#about us page
class BaseAboutus(TemplateView):
    template_name = "base/aboutus.html"

# -----------------------------------------------------------------------------------------------------

# Regional register

class BaseRegionalRegister(TemplateView):
    template_name = 'reguser/regionalregistration.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}) 

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the passwords
        if password != confirm_password:
            return self.render_to_response({'error': "Passwords do not match."})

        # Create the user
        user = User(username=username)
        user.set_password(password) 
        user.save() 
       
        user_group, created = Group.objects.get_or_create(name='area')
        user.groups.add(user_group)
        
        # Create a UserProfile for new user
        AreaProfile.objects.create(user=user,uname=user) 
        

        messages.success(request, "Registration successful! You can now log in.") 
        return redirect('home') 

        
        
    

# -----------------------------------------------------------------------------------------------------

# #Regional login 
class BaseRegionalLogin(LoginView):
    template_name = "login/regionallogin.html"
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form) 

    def get_success_url(self):
        return reverse_lazy('rdashboard')
    
 

# -----------------------------------------------------------------------------------------------------

# Doctor register

class BaseDoctorRegister(TemplateView):
    template_name = 'reguser/doctorregistration.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}) 

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the passwords
        if password != confirm_password:
            return self.render_to_response({'error': "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists in database.")
            return redirect('dregister')    

        # Create the user
        user = User(username=username)
        user.set_password(password) 
        user.save() 
       
        user_group, created = Group.objects.get_or_create(name='doctor')
        user.groups.add(user_group)
        
        # Create a UserProfile for new user
        DoctorProfile.objects.create(user=user,uname=user) 

        messages.success(request, "Registration successful! You can now log in.")        
        return redirect('home') 
        
    

# -----------------------------------------------------------------------------------------------------

# #Doctor login 
class BaseDoctorLogin(LoginView):
    template_name = "login/doctorlogin.html"
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form) 

    def get_success_url(self):
        return reverse_lazy('ddashboard')
    
 
# -----------------------------------------------------------------------------------------------------

# user register

class BaseUserRegister(TemplateView):
    template_name = 'reguser/userregistration.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}) 

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the passwords
        if password != confirm_password:
            return self.render_to_response({'error': "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists in database.")
            return redirect('uregister')    

        # Create the user
        user = User(username=username)
        user.set_password(password) 
        user.save() 
       
        user_group, created = Group.objects.get_or_create(name='user')
        user.groups.add(user_group)
        
        # Create a UserProfile for new user
        UserProfile.objects.create(user=user,uname=user)

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('home')
        
    

# -----------------------------------------------------------------------------------------------------

#user login 
class BaseUserLogin(LoginView):
    template_name = "login/userlogin.html"
    redirect_authenticated_user = False 

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form) 

    def get_success_url(self):
        return reverse_lazy('uprofile') 
    
# -----------------------------------------------------------------------------------------------------


#logout for all user 
class LogoutView(RedirectView):
    url = '/home'  
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)     


# --------------------------------------------------------------------------------------------------------
#home 
class BaseHome(TemplateView):
    template_name = "base/home.html"