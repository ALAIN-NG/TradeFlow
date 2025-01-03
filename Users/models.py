from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, name=None, role = 'C', **extra_fields):

        if not email:
            raise ValueError("L'adresse email doit être renseignée")
        
        email = self.normalize_email(email)

        user = self.model(name=name, email=email, role=role, **extra_fields)

        user.set_password(password)

        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password=None, name=None, age = 0, bp = 0000, **extra_fields):

        extra_fields.setdefault("is_staff", True)

        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, name=name, age = age, bp = bp,  **extra_fields)
    

class Person(AbstractBaseUser, PermissionsMixin):
    """
    Name: Person model definition
    Description: 
    author: ronelmaamoc52@gmail.com
    """
    SEX_TYPES = (
        ('M', _('Male')),
        ('F', _('Feminine')),
    )

    ROLE_TYPES = (
        ('S', _('Seller')),
        ('M', _('Manager')),
        ('C', _('Customer')),
        ('A', _('Admin')),
    )

    name = models.CharField(max_length=150)

    password = models.CharField(max_length=128)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=132)

    address = models.CharField(max_length=150)

    sex = models.CharField(max_length=1, choices = SEX_TYPES)

    age = models.PositiveIntegerField()

    city = models.CharField(max_length=32)

    bp = models.PositiveIntegerField()

    role = models.CharField(max_length=1, choices = ROLE_TYPES)

    crearted_date = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)

    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)



    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        """ Encrypt password before save """
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'password'], name = 'unique_person_name_password')
        ]
        verbose_name = "Person"
        verbose_name_plural = "Persons"
    
    def __str__(self):
        return f"{self.name} - {self.role}"
