import logging
import os
import uuid

import django
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #

class Workspace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    description = models.TextField("Description", blank=True)

    def __str__(self) -> str:
        return "Workspace" + str(self.id)


def get_request_constraint_upload_path(instance, filename):
    # instance is a Constraint
    ph = os.path.join(
        settings.MEDIA_ROOT,
        f"workspaces/{instance.request.workspace.id}/data/"
        f"{instance.request.req_uid}/constraints",
    )
    if not os.path.exists(ph):
        os.makedirs(ph)
    return (
        f"workspaces/{instance.request.workspace.id}/data/"
        f"{instance.request.req_uid}/constraints/" + filename
    )


class Constraint(models.Model):
    request = models.ForeignKey(
        "Request", on_delete=models.CASCADE, verbose_name="Request", default=None
    )
    file = models.FileField(
        "File", upload_to=get_request_constraint_upload_path, max_length=100
    )
    minimum = models.FloatField("Minimum")
    maximum = models.FloatField("Maximum")

    def __str__(self) -> str:
        return self.file.url


def get_request_shapefile_upload_path(instance, filename):
    # instance is a Request
    ph = os.path.join(
        settings.MEDIA_ROOT,
        f"workspaces/{instance.workspace.id}/data/{instance.req_uid}/shapefiles",
    )
    if not os.path.exists(ph):
        os.makedirs(ph)
    return (
        f"workspaces/{instance.workspace.id}/data/"
        f"{instance.req_uid}/shapefiles/" + filename
    )


def get_request_affarea_upload_path(instance, filename):
    # instance is a Request
    ph = os.path.join(
        settings.MEDIA_ROOT,
        f"workspaces/{instance.workspace.id}/data/{instance.req_uid}/shapefiles",
    )
    if not os.path.exists(ph):
        os.makedirs(ph)
    return (
        f"workspaces/{instance.workspace.id}/data/"
        f"{instance.req_uid}/" + filename
    )


class Request(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, verbose_name="Workspace", default=False
    )
    shp_file = models.FileField(
        "Shp File", upload_to=get_request_shapefile_upload_path, default=False
    )
    dbf_file = models.FileField(
        "Dbf File", upload_to=get_request_shapefile_upload_path, default=False
    )
    shx_file = models.FileField(
        "Shx File", upload_to=get_request_shapefile_upload_path, default=False
    )
    affected_area = models.FileField(
        "Affected area", upload_to=get_request_affarea_upload_path, default=False
    )
    travel_speed = models.FloatField("Travel speed (km/time step)", default=0)
    cell_size = models.FloatField("Cell size", default=0)
    req_uid = models.CharField("Unique ID", max_length=255, default="")
    create_date = models.DateTimeField("Created on", default=django.utils.timezone.now)

    def __str__(self) -> str:
        return "Workspace" + str(self.workspace.id) + " / Request" + str(self.id)


# --------------------------------------------------------------------------- #
# User helper methods (attached dynamically via User.add_to_class below)
# --------------------------------------------------------------------------- #

def send_reset_password_email(self):
    """Send a password-reset link to this user via email."""
    email_id = self.email
    email_name = self.username

    if not email_id:
        logger.warning(
            "Skipping password reset email for user %s: no email on file",
            email_name,
        )
        return

    domain = Site.objects.get_current().domain
    scheme = "http" if settings.DEBUG else "https"

    logger.debug(
        "Sending password reset email for user=%s to domain=%s",
        email_name,
        domain,
    )

    email_template = render_to_string(
        "email_reset_password.html",
        {
            "username": email_name,
            "url": f"{scheme}://{domain}/authenticate/password_reset/",
        },
    )
    email_obj = EmailMultiAlternatives(
        "DuduTracker: Password reset",
        "DuduTracker: Password reset",
        settings.EMAIL_HOST_USER,
        [email_id],
    )
    email_obj.attach_alternative(email_template, "text/html")
    email_obj.send(fail_silently=False)


def get_user_workspace(self):
    """Return the (first) workspace belonging to this user."""
    return Workspace.objects.filter(user=self).first()


User.add_to_class("send_reset_password_email", send_reset_password_email)
User.add_to_class("get_user_workspace", get_user_workspace)


# --------------------------------------------------------------------------- #
# Signals
# --------------------------------------------------------------------------- #

@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, update_fields, **kwargs):
    """
    - On first creation of a User: optionally send an invite/reset email.
    - Always ensure a Workspace exists for the user.

    NOTE: We only send the reset email on `created=True` (i.e. actual INSERT).
    This prevents accidental password-reset emails on every subsequent
    profile save, password change, admin edit, etc.
    """
    if created:
        # Only send an invite email when explicitly requested, e.g. by setting
        # `user._send_invite_email = True` before calling save() in an invite view.
        # Comment out / adjust if you want it to fire on *every* user creation.
        if getattr(instance, "_send_invite_email", False):
            try:
                instance.send_reset_password_email()
            except Exception:
                logger.exception(
                    "Failed to send reset email for user %s", instance.username
                )

    Workspace.objects.get_or_create(
        user=instance,
        defaults={"description": f"Workspace for {instance.username}"},
    )


@receiver(post_save, sender=Workspace)
def post_save_workspace(sender, instance, **kwargs):
    """Ensure the workspace data folder exists on disk."""
    workspace_path = os.path.join(settings.MEDIA_ROOT, f"workspaces/{instance.id}/data")
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)