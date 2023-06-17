from django.shortcuts import get_object_or_404, render,redirect,reverse
from . forms import *
from . models import *
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.db.models import Q




def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'index.html')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'adminclick.html')



def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'doctorclick.html')



def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'patientclick.html')

def admin_signup_view(request):
    form=AdminSigupForm()
    if request.method=='POST':
        form=AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'adminsignup.html',{'form':form})


def doctor_signup_view(request):
    userForm=DoctorUserForm()
    doctorForm=DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=DoctorUserForm(request.POST)
        doctorForm=DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm=PatientUserForm()
    patientForm=PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=PatientUserForm(request.POST)
        patientForm=PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient=patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patientsignup.html',context=mydict)


def aboutus_view(request):
    return render(request,'aboutus.html')



def contactus_view(request):
    sub = ContactusForm()
    if request.method == 'POST':
        sub = ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'contactsuccess.html')
    return render(request, 'contactus.html', {'form':sub})



#-----------for checking user is doctor , patient or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval=Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request,'doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval=Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request,'patient_wait_for_approval.html')



#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard
    doctors= Doctor.objects.all().order_by('-id')
    patients=Patient.objects.all().order_by('-id')
    #for three cards
    doctorcount=Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=Doctor.objects.all().filter(status=False).count()

    patientcount=Patient.objects.all().filter(status=True).count()
    pendingpatientcount=Patient.objects.all().filter(status=False).count()

    appointmentcount=Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=Appointment.objects.all().filter(status=False).count()
    mydict={
    'doctors':doctors,
    'patients':patients,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'admin_dashboard.html',context=mydict)

# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'admin_doctor.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors= Doctor.objects.all().filter(status=True)
    return render(request,'admin_view_doctor.html',{'doctors':doctors})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    user=User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    user=User.objects.get(id=doctor.user_id)

    userForm=DoctorUserForm(instance=user)
    doctorForm=DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=DoctorUserForm(request.POST,instance=user)
        doctorForm=DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'admin_update_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=DoctorUserForm()
    doctorForm=DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=DoctorUserForm(request.POST)
        doctorForm=DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'admin_add_doctor.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=Doctor.objects.all().filter(status=False)
    return render(request,'admin_approve_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=Doctor.objects.get(id=pk)
    user=User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=Doctor.objects.all().filter(status=True)
    return render(request,'admin_view_doctor_specialisation.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=Patient.objects.all().filter(status=True)
    return render(request,'admin_view_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)

    userForm=PatientUserForm(instance=user)
    patientForm=PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=PatientUserForm(request.POST,instance=user)
        patientForm=PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=PatientUserForm()
    patientForm=PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=PatientUserForm(request.POST)
        patientForm=PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=Patient.objects.all().filter(status=False)
    return render(request,'admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=Patient.objects.all().filter(status=True)
    return render(request,'admin_discharge_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=Patient.objects.get(id=pk)
    days=(date.today()-patient.admitDate) #2 days, 0:00:00
    assignedDoctor=User.objects.all().filter(id=patient.assignedDoctorId)
    d=days.days # only how many day that is 2
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'patient_final_bill.html',context=patientDict)
    return render(request,'patient_generate_bill.html',context=patientDict)

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def generate_vaccine_certi(request,pk):
    
    vaccination = Vaccineappointmentdetails.objects.get(id=pk)
    patient=Patient.objects.get(id=pk)
    patientDict={
        'patientId':pk,
        'name':vaccination.patientName,
        'vaccine': vaccination.vaccine,
        'date': vaccination.date,
    
    }
    if request.method == 'POST':
       pDD=Vaccineappointmentdetails()
       pDD.patientId=pk
       pDD.patientName= vaccination.patientName
       pDD.vaccine = vaccination.vaccine
       pDD.date = vaccination.date
       pDD.save()
       return render(request,'patient_generate_vaccine_certi.html',context=patientDict)
    
    return render(request,'patient_generate_vaccine_certi.html',context=patientDict)







#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import urllib
import base64


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
   
    pdf_file  = io.BytesIO()
    pisa.CreatePDF(html.encode('UTF-8'), dest=pdf_file)
    pdf_data = pdf_file.getvalue()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_pdf.pdf"'
    response.write(pdf_data)

    return response


def get_image_data(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image_data).decode('utf-8')


def download_pdf_view(request,pk):
    dischargeDetails=PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('download_bill.html',dict)

def download_pdf_view2(request,pk):
    vaccination = Vaccineappointmentdetails.objects.get(id=pk)

    dict = {
       'name':vaccination.patientName,
        'vaccine': vaccination.vaccine,
        'date': vaccination.date,
        'image_data': get_image_data('static/images/vaccine.png'),
        'image_data1': get_image_data('static/images/logo1.png'),
    }

    return render_to_pdf('download_vaccine_certificate.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=Appointment.objects.all().filter(status=True)
    return render(request,'admin_view_appointment.html',{'appointments':appointments})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_vaccine_appointment_view(request):
    return render(request,'admin_vaccine_appointment.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_vaccine_appointment_details_view(request):
    vaccinations= Vaccineappointmentdetails.objects.all().filter(status=True)
    return render(request,'admin_vaccine_appointment_details.html',{'vaccinations':vaccinations})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_generate_vaccine_certi_view(request):
    vaccinations= Vaccineappointmentdetails.objects.all().filter(status=True)
    return render(request,'admin_generate_vaccine_certi.html',{'vaccinations':vaccinations})
    

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=Appointment.objects.all().filter(status=False)
    return render(request,'admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'doctor_dashboard.html',context=mydict)






@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'doctor_patient.html',context=mydict)





@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_prescription(request):

    prescriptionForm= PatientPrescriptionForm()
    mydict={'prescriptionForm':prescriptionForm, 'doctor':Doctor.objects.get(user_id=request.user.id)}

       
    if request.method=='POST':
        prescriptionForm = PatientPrescriptionForm(request.POST)
        if prescriptionForm.is_valid():
            prescription = prescriptionForm.save(commit=False)
         
            prescription.patientId=request.POST.get('patientId')

            prescription.patientName=User.objects.get(id=request.POST.get('patientId')).first_name
            prescription.status=True
            prescription.save()
        return HttpResponseRedirect('doctor-view-prescription')

    
    return render(request,'doctor_patient_prescription.html',context=mydict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def vaccination_appointment_book_view(request):

    vaccineForm = VaccinationForm()
    mydict = {'vaccineForm' : vaccineForm, 'patient' : Patient.objects.get(user_id = request.user.id)}

    if request.method=='POST':
        vaccineForm = VaccinationForm(request.POST);
        if vaccineForm.is_valid():
            vaccination = vaccineForm.save(commit=False)
            vaccination.patientId= request.POST.get('patientId')
            vaccination.patientName = User.objects.get(id=request.POST.get('patientId')).first_name
            vaccination.status = True
            vaccination.save()
        return HttpResponseRedirect('vaccine-view-appointment')
    
    
    return render(request,'vaccine_book_appointment.html',context=mydict)




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def vaccine_view_appointment(request):

    mydict={
        'patient':Patient.objects.get(user_id = request.user.id),
        'vaccinations' : Vaccineappointmentdetails.objects.all().filter(status=True,patientId=request.user.id)
    }

    return render(request,'vaccine_view_appointment.html',context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_prescription(request):
  
    mydict={
    'doctor':Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
     'prescriptions' : Prescriptiondetails.objects.all().filter(status=True)
    }
    return render(request,'doctor_view_prescription.html',context=mydict)




#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------



#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient= Patient.objects.get(user_id=request.user.id)
    doctor= Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name,
    'doctorMobile':doctor.mobile,
    'doctorAddress':doctor.address,
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'patient_dashboard.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient= Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm= PatientAppointmentForm()
    patient= Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm= PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor= Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName= User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request,'patient_book_appointment.html',context=mydict)



def patient_view_doctor_view(request):
    doctors= Doctor.objects.all().filter(status=True)
    patient= Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'patient_view_doctor.html',{'patient':patient,'doctors':doctors})



def search_doctor_view(request):
    patient= Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors= Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient= Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments= Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'patient_view_appointment.html',{'appointments':appointments,'patient':patient})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient= Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails= PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'patient_discharge.html',context=patientDict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_vaccine_view(request):
    patient= Patient.objects.get(user_id=request.user.id)
    
    vaccination = Vaccineappointmentdetails.objects.all().filter(id=patient.id)
    dict = None
    if vaccination :
       vaccination = Vaccineappointmentdetails.objects.get(id=patient.id)
       dict = {
        'patient':patient,
        'patientId':patient.id,
        'is_vaccinated' :True,
        'name':vaccination.patientName,
        'vaccine': vaccination.vaccine,
        'date': vaccination.date,
        'image_data': get_image_data('static/images/vaccine.png'),
        'image_data1': get_image_data('static/images/logo1.png'),
       }
    else :
       dict={
            'patient':patient,
            'is_vaccinated':False,
            'patient':patient,
            'patientId':request.user.id,
       }
    return render(request,'patient_vaccine.html',context=dict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_prescription(request):
  
    mydict={
    'patient': Patient.objects.get(user_id=request.user.id), #for profile picture
    'prescriptions' : Prescriptiondetails.objects.all().filter(status=True,patientId=request.user.id)
    }
    return render(request,'patient_view_prescription.html',context=mydict)







@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def vaccination_appointment_view(request):
    mydict={
    'patient': Patient.objects.get(user_id=request.user.id), #for profile picture
    }
    
    return render(request,'vaccination_appointment.html',context=mydict)

#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------



