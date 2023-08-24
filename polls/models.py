import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    def __str__(self):
        return self.question_text
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
    
class Message(models.Model):
	content = models.TextField()
        
class CustomUserManager(BaseUserManager):
  def create_user(self, name, password=None, **extra_fields):
      if not name:
          raise ValueError("The Name field must be set")
      user = self.model(name=name, **extra_fields)
      user.set_password(password)
      user.save(using=self._db)
      return user
  def get_by_natural_key(self, name):
      return self.get(name=name)
        
class User(models.Model):
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def check_password(self, raw_password):
        # Implement your password comparison logic
        return raw_password == self.password
    
    def __str__(self):
        return self.name

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    