from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from .models import *
from django.db import transaction
import pdfkit
from django.template.loader import get_template
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import pagination
from django.utils.translation import gettext as _


class SignupView(View):

    templates_name = 'signup.html'
    def get(self, request):
        return render(request, self.templates_name)
    
    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        sex = request.POST.get("sex")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        age = request.POST.get("age")
        city = request.POST.get("city")
        bp = request.POST.get("bp")

        # Create a user with role 'Customer'
        user = Person.objects.create(
            name=name,
            email=email,
            password=password,
            sex=sex,
            phone=phone,
            address=address,
            age=age,
            city=city,
            role='C',
            bp = bp,
            is_active=True
        )
        return redirect('login')  # Redirection on the login page after signup


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Assurez-vous que vous utilisez un backend personnalisé pour email
            user = authenticate(request, username=email, password=password)  
            
            if user is not None:
                login(request, user)

                # Redirigez selon le rôle de l'utilisateur
                role_redirects = {
                    'S': 'seller-dashboard',
                    'A': 'admin-dashboard',
                    'M': 'manager-dashboard',
                    'C': 'customer-home'
                }
                return redirect(role_redirects.get(user.role, 'default-dashboard'))

            else:
                messages.error(request, "Email ou mot de passe incorrect.")
        
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        
        return render(request, self.template_name, {'error': 'Email ou mot de passe incorrect.'})

class PersonView(LoginRequiredMixin, View):
    """ Main view """

    templates_name = 'person-view.html'

    persons = Person.objects.all().order_by('id')

    page = 'person-view/'

    context = {
        'persons': persons,
        'page' : page
    }

    def get(self, request, *args, **kwargs):

        items = pagination(request, self.persons)

        self.context['persons'] = items

        return render(request, self.templates_name, self.context)
    
    
    def post(self, request, *args, **kwargs):


        # deleting a person

        if request.POST.get('id_supprimer'):

            try:

                obj = Person.objects.get(pk = request.POST.get('id_supprimer'))
                obj.delete()

                messages.success(request, _("The deletion was successful."))
            
            except Exception as e:

                messages.error(request, f"Sorry, the following error has occurred {e}.")

        items = pagination(request, self.persons)

        self.context['persons'] = items

        return render(request, self.templates_name, self.context)


class AddCustomerView(LoginRequiredMixin, View):
    """ add new customer """

    page = 'add-customer/'

    context = {
        'page' : page
    }
    templates_name = 'add-customer.html'

    def get(self, request, *args, **kwargs):
        
        return render(request, self.templates_name, self.context)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'city': request.POST.get('city'),
            'bp': request.POST.get('zip'),
            'role': 'C',
            # 'save_by': request.user
        }


        try:
            created = Person.objects.create(**data)

            if created:
                messages.success(request, _("Customer registered successfully."))
                
                if request.user.role == 'S':
                    return redirect('home')
                else:
                    return redirect('manage-clients')

            else:
                messages.error(request, "sorry, pleace try again, the sent data is corrupt.")

        except Exception as e:
            messages.error(request, f"Sorry our system is detecting the following issues {e}.")

        return render(request, self.templates_name)


class AddSellerView(LoginRequiredMixin, View):
    """ add new seller """

    page = 'add-seller/'

    context = {
        'page' : page
    }
    templates_name = 'add-seller.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.templates_name, self.context)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'city': request.POST.get('city'),
            'bp': request.POST.get('zip'),
            'role': 'S',
        }

        try:
            created = Person.objects.create(**data)

            if created:
                messages.success(request, _("Seller registered successfully."))
                return redirect('manage-sellers')

            else:
                messages.error(request, "sorry, pleace try again, the sent data is corrupt.")

        except Exception as e:
            messages.error(request, f"Sorry our system is detecting the following issues {e}.")

        return render(request, self.templates_name)


class AddManagerView(LoginRequiredMixin, View):
    """ add new manager """

    page = 'add-manager/'

    context = {
        'page' : page
    }
    templates_name = 'add-manager.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.templates_name, self.context)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'city': request.POST.get('city'),
            'bp': request.POST.get('zip'),
            'role': 'M',
        }

        try:
            created = Person.objects.create(**data)

            if created:
                messages.success(request, _("Manager registered successfully."))
                return redirect('manage-managers')

            else:
                messages.error(request, "sorry, pleace try again, the sent data is corrupt.")

        except Exception as e:
            messages.error(request, f"Sorry our system is detecting the following issues {e}.")

        return render(request, self.templates_name)


class UpdatePersonView(LoginRequiredMixin, View):
    """ View to update an existing person """

    template_name = 'update-person.html'

    def get(self, request, pk, *args, **kwargs):
        try:
            person = Person.objects.get(id=pk)
            # person.password = make_password(person.password)
            page = f'update-person/{pk}/'

            context = {
                'person': person,
                'page': page
            }
            return render(request, self.template_name, context)
        
        except Person.DoesNotExist:
            messages.error(request, "Person not found.")
            return redirect('person-view')

    def post(self, request, pk, *args, **kwargs):
        try:
            person = Person.objects.get(id=pk)

            # Mise à jour des champs de l'objet person
            person.name = request.POST.get('name')
            person.email = request.POST.get('email')
            person.phone = request.POST.get('phone')
            person.password = request.POST.get('password')
            person.password = make_password(person.password)
            person.sex = request.POST.get('sex')
            person.age = request.POST.get('age')
            person.address = request.POST.get('address')
            person.city = request.POST.get('city')
            person.bp = request.POST.get('zip')

            person.save()

            messages.success(request, _("Person updated successfully."))
            return redirect('person-view')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('update-person', pk=pk)
