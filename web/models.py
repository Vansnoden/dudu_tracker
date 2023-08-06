from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
import os
import uuid
import django

class Workspace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    description = models.TextField("Description", blank=True)

    def __str__(self) -> str:
        return "Workspace"+str(self.id)


def get_request_constraint_upload_path(instance, filename):
    # constraint
    ph = os.path.join(settings.MEDIA_ROOT, f"workspaces/{instance.request.workspace.id}/data/{instance.request.req_uid}/constraints")
    if not os.path.exists(ph):
        os.makedirs(ph)
    return f"workspaces/{instance.request.workspace.id}/data/{instance.request.req_uid}/constraints/"+filename


class Constraint(models.Model):
    request = models.ForeignKey("Request", on_delete=models.CASCADE, verbose_name="Request", default=None)
    file = models.FileField("File", upload_to=get_request_constraint_upload_path, max_length=100)
    minimum = models.FloatField("Minimum")
    maximum = models.FloatField("Maximum")

    def __str__(self) -> str:
        return self.file.url


def get_request_shapefile_upload_path(instance, filename):
    # instance is a Request
    ph = os.path.join(settings.MEDIA_ROOT, f"workspaces/{instance.workspace.id}/data/{instance.req_uid}/shapefiles")
    if not os.path.exists(ph):
        os.makedirs(ph)
    return f"workspaces/{instance.workspace.id}/data/{instance.req_uid}/shapefiles/"+filename


def get_request_affarea_upload_path(instance, filename):
    # instance is a Request
    ph = os.path.join(settings.MEDIA_ROOT, f"workspaces/{instance.workspace.id}/data/{instance.req_uid}/shapefiles")
    if not os.path.exists(ph):
        os.makedirs(ph)
    return f"workspaces/{instance.workspace.id}/data/{instance.req_uid}/"+filename


class Request(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, verbose_name="Workspace", default=False)
    shp_file = models.FileField("Shp File", upload_to=get_request_shapefile_upload_path, default=False)
    dbf_file = models.FileField("Dbf File", upload_to=get_request_shapefile_upload_path, default=False)
    shx_file = models.FileField("Shx File", upload_to=get_request_shapefile_upload_path, default=False)
    affected_area = models.FileField("Affected area", upload_to=get_request_affarea_upload_path, default=False)
    travel_speed = models.FloatField("Travel speed (km/time step)", default=0)
    cell_size = models.FloatField("Cell size", default=0)
    req_uid = models.CharField("Unique ID", max_length=255, default="")
    create_date = models.DateTimeField("Created on", default=django.utils.timezone.now)

    def __str__(self) -> str:
        return "Workspace"+str(self.workspace.id)+" / Request"+str(self.id)



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
def post_save_user(sender, instance, **kwargs):
    if instance.id and not kwargs['update_fields']:
        print(kwargs)
        instance.send_reset_password_email()
    new_workspace = Workspace(
        user=instance,
        description=f"Workspace for {instance.username}"
    )
    existing_workspace = Workspace.objects.filter(user=instance)
    if not existing_workspace:
        new_workspace.save()

def get_user_workspace(self):
    existing_workspace = Workspace.objects.filter(user=self)
    return existing_workspace[0]

User.add_to_class("send_reset_password_email", send_reset_password_email)
User.add_to_class("get_user_workspace", get_user_workspace)


@receiver(post_save,sender=Workspace)
def post_save_workspace(sender, instance, **kwargs):
    """checkif workspace folder exist if not create one"""
    workspace_path = os.path.join(settings.MEDIA_ROOT, f"workspaces/{instance.id}/data")
    # gridFilesLocation = os.path.join(settings.MEDIA_ROOT, f"workspaces/{instance.id}/data/gridFiles")
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        # os.makedirs(gridFilesLocation)