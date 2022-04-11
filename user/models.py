from django.db import models
import base64
import secrets
import string

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager, AbstractUser, User
from django.db import models
from django.utils.translation import gettext_lazy as _


class LifeCycleModel(models.Model):
    lc_status = models.CharField(max_length=20, null=True, default='')
    lc_start_date = models.DateTimeField(null=True, auto_now_add=True)
    lc_end_date = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class Member(LifeCycleModel):
    """
    An abstract base class implementing a fully featured User model

    Password and date/time of last login are given from AbstractBaseUser.
    """

    # Data fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=200, null=False, blank=True, unique=True)
    nickname = models.CharField(max_length=200, null=True, blank=True)
    is_staff = models.BooleanField(null=False, blank=False, default=False)
    date_joined = models.DateTimeField(null=True, editable=False)

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'member'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_joined = timezone.now()
        self.last_login = timezone.now()
        return super(Member, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    def __iter__(self):
        yield 'id', self.id
        yield 'username', self.username
        yield 'nickname', self.nickname
        yield 'is_staff', self.is_staff
        yield 'is_superuser', self.is_superuser
        yield 'last_login', self.last_login
        yield 'date_joined', self.date_joined


class MemberProfile(LifeCycleModel):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='user_profile')
    time_zone = models.CharField(max_length=50, default='')
    # interest_category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE,
    #                                       db_column='interest_category_id', null=True)
    signup_source = models.CharField(max_length=50, default='')
    language_code = models.CharField(max_length=3, default='')
    nationality_country_code = models.CharField(max_length=2, default='')

    # subscription_path = models.ForeignKey(UserSubsriptionPath, on_delete=models.CASCADE, db_column='subscription_path_id', null=True)
    # user_event_code = models.ForeignKey(UserEventCode, on_delete=models.CASCADE, db_column='user_event_code_id', null=True)
    class Meta:
        db_table = 'member_profile'



class Token(LifeCycleModel):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='user_profile')
    time_zone = models.CharField(max_length=50, default='')
    # interest_category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE,
    #                                       db_column='interest_category_id', null=True)
    signup_source = models.CharField(max_length=50, default='')
    language_code = models.CharField(max_length=3, default='')
    nationality_country_code = models.CharField(max_length=2, default='')

    # subscription_path = models.ForeignKey(UserSubsriptionPath, on_delete=models.CASCADE, db_column='subscription_path_id', null=True)
    # user_event_code = models.ForeignKey(UserEventCode, on_delete=models.CASCADE, db_column='user_event_code_id', null=True)
    class Meta:
        db_table = 'member_profile'
