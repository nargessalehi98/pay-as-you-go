from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import ASCIIUsernameValidator


class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError(_('Username must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    username_validator = ASCIIUsernameValidator()

    id = models.BigAutoField(db_column='ID', primary_key=True)
    username = models.CharField(db_column='Username', max_length=15, unique=True, validators=[username_validator],
                                help_text=_('Required. 31 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                error_messages={'unique': _('A user with this username already exists.')})

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'User'

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])


class RequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField()
    count = models.DecimalField(max_digits=8, decimal_places=1, default=0.0)
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=0.000)
