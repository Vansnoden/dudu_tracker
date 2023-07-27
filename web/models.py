from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
from django.db.models.signals import post_save

# Create your models here.
class Constraint(models.Model):
    file = models.FileField("File", upload_to="uploads/constraints", max_length=100)
    minimum = models.FloatField("Minimum")
    maximum = models.FloatField("Maximum")
    user_data_id = models.ForeignKey("UserData", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.file.url

class UserData(models.Model):
    project_folder = models.TextField("Project folder")
    shp_file = models.FileField("Shp File")
    dbf_file = models.FileField("Dbf File")
    shx_file = models.FileField("Shx File")
    travel_speed = models.FloatField("Travel speed (km/time step)", default=0)
    cell_size = models.FloatField("Cell size", default=0)

    def __str__(self) -> str:
        return self.project_folder
    


def send_reset_password_email(self):
    email_id = self.email
    email_name = self.username
    domain = Site.objects.get_current().domain
    print(f"DOMAIN: {domain}")

    email_template = render_to_string(
        'email_reset_password.html', {
            "username": email_name,
            "url": f"{domain}/authenticate/password_reset/",
        })
    email_obj = EmailMultiAlternatives(
        "DuduTracker: Password reset",
        "DuduTracker: Password reset",
        settings.EMAIL_HOST_USER,
        [email_id],
    )
    email_obj.attach_alternative(email_template, 'text/html')
    email_obj.send()
    

@receiver(post_save,sender=User)
def post_save(sender, instance, **kwargs):
    if instance.id and not kwargs['update_fields']:
        print(kwargs)
        instance.send_reset_password_email()


User.add_to_class("send_reset_password_email", send_reset_password_email)
# User.add_to_class("save", save)