from django.db import models
from pydantic import BaseModel # for models not to be saved in the DB
from typing import Tuple

# Create your models here.
class Constraint(BaseModel):
    file_path: str
    minimun: float
    maximun: float


class UserData(BaseModel):
    project_folder: str
    shp_file: str
    dbf_file: str
    shx_file: str
    constraints: list[Constraint]