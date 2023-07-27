from django.db import models


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
    