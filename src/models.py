from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    name = models.TextField(verbose_name='Username', null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(null=False)
    is_bot = models.BooleanField(default=False)
    tg_id = models.CharField(null=False)

    def __str__(self):
        return f"Profile-{self.pk}_{self.name}"


class Message(models.Model):

    body = models.TextField(null=False, default="Empty body")
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(null=False, default="Empty response")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message-{self.pk}__from_{self.sender.name}"
