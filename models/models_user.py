import base64
import importlib
import secrets
import string
import threading

from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from main.globals import YALLIYALLI, STATUS_INPROGRESS, STATUS_INACTIVE
from main.models_baseinfo import LifeCycleModel


def encode_secret(user, code):
    return base64.b64encode((user.username + ':' + code).encode('utf-8')).decode('utf-8')


def decode_secret(secret):
    username, code = base64.b64decode(secret.encode('utf-8')).decode('utf-8').split(':')
    users = User.objects.filter(username__iexact=username)
    return users and users[0] or None, code


def random_string(length=settings.USERS_VERIFICATION_CODE_LENGTH):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


class CustomUserManager(BaseUserManager):
    def create_user(self, **extra_fields):
        user = self.model(**extra_fields)
        password = extra_fields.get('password', '')
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        user = self.create_user(username=username, password=password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email_):
        return self.get(email=email_)


class User(AbstractBaseUser, PermissionsMixin, LifeCycleModel):
    """
    An abstract base class implementing a fully featured User model

    Password and date/time of last login are given from AbstractBaseUser.
    """

    # Data fields
    username = models.CharField(max_length=200, null=False, blank=True, unique=True)
    nickname = models.CharField(max_length=200, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=200, null=False, blank=True)
    middle_name = models.CharField(max_length=200, null=False, blank=True)
    last_name = models.CharField(max_length=200, null=False, blank=True)
    email = models.EmailField(max_length=200, null=False, blank=True, db_index=True)
    verification = models.CharField(max_length=50, null=True)
    is_staff = models.BooleanField(null=False, blank=False, default=False)
    is_dormant = models.BooleanField(null=False, blank=False, default=False)
    dormant_date = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(null=True, editable=False)
    email_verification = models.CharField(max_length=settings.USERS_VERIFICATION_CODE_LENGTH, null=False, blank=True,
                                          default=random_string)
    password_reset = models.CharField(max_length=settings.USERS_VERIFICATION_CODE_LENGTH, null=False, blank=True,
                                      default='')
    meet_access_token = models.CharField(max_length=200, null=True, blank=True)
    refresh_token = models.TextField(default='', null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_joined = timezone.now()
        self.last_login = timezone.now()
        return super(User, self).save(*args, **kwargs)

    # 이메일 인증 전 기가입
    @classmethod
    def pre_save(self, verification, email):
        user = User.objects.create(
            username=email,
            first_name='',
            middle_name='',
            last_name='',
            email=email,
            verification=verification,
            is_staff=False,
            is_dormant=False,
            email_verification='',
            password_reset='',
            lc_start_date=timezone.now(),
            lc_status=STATUS_INPROGRESS
        )

        return user

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return self.email

    def __iter__(self):
        yield 'id', self.id
        yield 'username', self.username
        yield 'first_name', self.first_name
        yield 'last_name', self.last_name
        yield 'email', self.email
        yield 'is_staff', self.is_staff
        yield 'is_active', self.is_active
        yield 'is_superuser', self.is_superuser
        yield 'last_login', self.last_login
        yield 'date_joined', self.date_joined

    # Password reset
    def __send_mail(self, callback, value, system=None, language=None):
        try:
            module, function = callback
            imported_module = importlib.import_module(module)
            subject, message, html_message = getattr(imported_module, function)(self, value, system, language)
        except:
            return False

        try:
            using_thread = settings.USERS_SEND_EMAIL_USING_THREAD
        except:
            using_thread = False

        try:
            if using_thread:
                if system == YALLIYALLI:
                    thread = threading.Thread(target=send_email_from_change,
                                              args=(subject, message, html_message, self.username, system))
                    thread.start()
                else:
                    thread = threading.Thread(target=send_mail, kwargs={
                        'subject': subject,
                        'message': message,
                        'from_email': settings.DEFAULT_FROM_EMAIL,
                        'recipient_list': [self.username],
                        'fail_silently': True,
                        'html_message': html_message,
                    })
                    thread.start()

                return True
            else:
                return send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL,
                                 recipient_list=[self.username], fail_silently=True, html_message=html_message) > 0
        except Exception as ex:
            print('ex:', ex)

    def verify_email(self, code=None):
        """
        When a new user record is created, its email address is not verified.  This function sends an email to the email
        address in the record with a secret code to see if the email address is valid.  If this function is invoked with
        the secret code, the email address is validated correctly.

        :param code: Secret code for email address verification - request for sending en email if None is given
        :return:
            None if the email has already been verified
            True if sending the verification email is successful or if verification is successful
            False if sending the verification email failed or if verification failed
        """
        if not self.email_verification:
            return None
        elif not code:  # Send an email to user's email address to confirm the email address.
            secret = encode_secret(self, self.email_verification)
            return self.__send_mail(settings.USERS_EMAIL_FOR_EMAIL_VERIFICATION, secret)
        else:
            if self.email_verification == code:  # The email address has been correctly validated.
                self.email_verification = ''
                self.save()
                return True
            else:  # The email address has not been correctly validated.
                return False

    def reset_password(self, code=None, system=None, language=None):
        """
        When a user forgets his/her password, he/she can request the password reset.

        :param code: Secret code for password reset
        :return:
            True if sending the password reset email is successful or if reset request confirmation is successful
            False if sending the password reset email failed or if reset request confirmation failed
        """
        if not code:  # Send an email to confirm the user's request for resetting the password.
            self.password_reset = random_string()
            self.save()
            secret = encode_secret(self, self.password_reset)
            return self.__send_mail(settings.USERS_EMAIL_FOR_PASSWORD_RESET_REQUEST, secret, system, language)
        else:
            if self.password_reset and self.password_reset == code:
                # The request for resetting the password has been confirmed.  A random string is generated and sent to
                # user's email address.
                self.password_reset = ''
                random_password = random_string(settings.USERS_RANDOM_PASSWORD_LENGTH)
                self.set_password(random_password)
                self.save()
                # Send an email to tell the random password.
                return self.__send_mail(settings.USERS_EMAIL_FOR_PASSWORD_RESET_RESULT, random_password, system,
                                        language)
            else:
                return False


def send_email_from_change(subject, message, html_message, user_email, system):
    # YalliYalli
    if system == YALLIYALLI:
        try:
            # from email setting - no-reply@yalliyalli.com
            settings.EMAIL_HOST = settings.SES_EMAIL_HOST
            settings.EMAIL_HOST_USER = settings.SES_EMAIL_HOST_USER
            settings.EMAIL_HOST_PASSWORD = settings.SES_EMAIL_HOST_PASSWORD

            if settings.DEBUG:
                msg = EmailMultiAlternatives(subject, message, settings.YALLIYALLI_FROM_EMAIL,
                                             [user_email, 'minkyu.lee@ebridge-world.com'])
            else:
                msg = EmailMultiAlternatives(subject, message, settings.YALLIYALLI_FROM_EMAIL,
                                             [user_email, 'minkyu.lee@ebridge-world.com'])
            msg.attach_alternative(html_message, "text/html")
            msg.send()

            # restore from email setting - no-reply@ebridge-world.com
            settings.EMAIL_HOST = settings.EBRIDGE_EMAIL_HOST
            settings.EMAIL_HOST_USER = settings.EBRIDGE_EMAIL_HOST_USER
            settings.EMAIL_HOST_PASSWORD = settings.EBRIDGE_EMAIL_HOST_PASSWORD

        except Exception as ex:
            print('ex:', ex)
