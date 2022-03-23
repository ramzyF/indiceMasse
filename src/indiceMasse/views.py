from asyncio.windows_events import NULL
import datetime
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Formation import settings 
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf
import os
from django.template.loader import get_template

# Create your views here.
def home(request):
  context = {}
  
  return render(request, 'index.html', context)
  from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template


def signup(request):
  form = CreatePatientForm()
  if request.method == 'POST':
    form = CreatePatientForm(request.POST)
    if form.is_valid():
      form.save()
      form = CreatePatientForm()
      return redirect('signin')
      
    
  context = {
      'form': form, 
    
  }
  
  return render(request, 'register_page.html',context)

def signin(request): 
  message = ''
  form = CreatePatientForm()
  if request.method == 'POST':
    form = CreatePatientForm(request.POST)
    email = form['email'].value()
    password = form['password1'].value()
    patient = authenticate(request, email=email, password=password)  
    if patient is not None and patient.is_active:
      login(request, patient)
      return redirect('home')
    else:
      message ='Veuillez entrer correctement vos identifiants\ncar soit vous n\'avez pas de compte ou les identifiants sont incorrects !'
  context={
    'form':form,
    'message':message
  }
  return render(request, 'login_page.html', context)

@login_required
def signout(request):
  logout(request)
  return redirect('home')

def ImcVal(imc):
  if imc < 18.5:
    return {'statut': 'Maigre', 'conseil':'Lorem ipsum dolor sit amet'}
  elif 18.5 <= imc <= 25:
    return {'statut': 'Normale', 'conseil':'Lorem ipsum dolor sit amet'}
  else:
    return {'statut': 'Obèse', 'conseil':'Lorem ipsum dolor sit amet'}

@login_required
def getImc(request):
  are_valid=True
  message = []
  imc = 0
  if request.method == 'POST':
    poids = str(request.POST['poids'])
    taille = str(request.POST['taille'])
    poids = poids.replace(',', '.')
    taille = taille.replace(',', '.')
    poids = poids.replace(';', '.')
    taille = taille.replace(';', '.')
    if len(poids) == 5:
      if not('.' == poids[2] and poids[:2].isdecimal() and poids[3:].isdecimal() and poids != '00,00'):
        message.append('Veuillez entrer un poids valide de la forme 03.33, 100.00 par exmple')
        are_valid = False
    elif len(poids) == 6:
      if not('.' == poids[3] and poids[:3].isdecimal() and poids[4:].isdecimal() and poids != '000,00'):
        message.append('Veuillez entrer un poids valide de la forme 03.33, 100.00 par exmple')
        are_valid = False
    else:
      message.append('Veuillez entrer un poids valide de la forme 03.33, 100.00 par exmple')
      are_valid = False
    if not(len(taille) == 5 and'.' == taille[2] and taille[:2].isdecimal() and taille[3:].isdecimal() and taille != '00,00'):
        message.append('Veuillez entrer une taille valide de la forme 03.33 par exmple')
        are_valid = False
    
    if are_valid:
      imc = float(poids)/(float(taille)**2)
      imc =  round(imc, 2)
      #generons le pdf
      result = ImcVal(imc)
      context={
        'username': request.user.name,
        'city': request.user.city,
        'imc': str(imc),
        'statut': result['statut'],
        'conseil': result['conseil'],
      }
      pdf = render_to_pdf('pdf/report.html', context)
      ''' if os.path.exists(request.user.report.path):
        os.remove(request.user.report.path)
        request.user.report = NULL#on supprime le fichier de la bd pour accueillir un new file
        request.user.save() '''
      request.user.report = pdf
      request.user.save() 
      #fin pdf
      textMessage = 'Salut ' + str(request.user.name)+' !'+'\nCi-joint le resultat de votre IMC.\n\n\nMerci d\'avoir visiter notre site.'
      #l'envoi du mail
      email_subject = 'MON IMC'
      email_message = textMessage 
      from_email = settings.EMAIL_HOST_USER
      to_email = [request.user.email]
      mail = EmailMessage(email_subject, email_message, from_email, to_email)
      mail.attach_file(request.user.report.path)
      mail.fail_silently = False
      mail.send()
      #fin du mail
      
      #envoi par whatsapp
      from twilio.rest import Client
      account_sid = '' 
      auth_token = '' 
      client = Client(account_sid, auth_token) 
      textW ='Salut ' + request.user.name +'\n\nVotre IMC: ' + str(imc)+'Kg/m2'
      textW += '\nStatut: ' + result['statut'] + '\n\nConseil: ' + result['conseil']           
      textW += '\n\n\n\nMerci\nhttps://monimc.com'
      messageW = client.messages.create( 
        from_='whatsapp:+14155238886',
        body= textW ,      
        to='whatsapp:'+ request.user.tel_number
      ) 
 
      
      #fin whatsqpp
  context={
    'messages':message,
    'success':are_valid
  }
  return render(request, 'calcul.html', context)

 


''' class GeneratePdf(View):
  def get(self, request, *args, **kwargs):
    context = {
      'today': datetime.datetime.today(), 
      'amount': 39.99,
      'customer_name': 'Cooper Mann',
      'order_id': 1233434,
    }
    pdf = render_to_pdf('pdf/invoice.html', context)
    if pdf:
      response = HttpResponse(pdf, content_type='application/pdf')
      filename = "imc_%s.pdf" %("12341231")
      #content = "inline; filename=%s" %(filename)
      download = request.GET.get("download")
      #if download:
      content = "attachment; filename=%s" %(filename)
      response['Content-Disposition'] = content
      print("reponse ",response)
      return response
    
    return HttpResponse("Not found")
   

 '''