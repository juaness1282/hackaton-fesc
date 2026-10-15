from typing import Literal
from pydantic import BaseModel

class Organization(BaseModel):
    id:str | None
    name:str | None

class Member(BaseModel):
    document:str
    fullName:str
    status:Literal["ACTIVE","RETIRED","SUSPENDED"]
    company:Organization

class Beneficiary(BaseModel):
    document:str
    fullName:str
    relationship:Literal["SPOUSE","CHILD","FATHER","MOTHER"]

class Company(BaseModel):
    id:str
    name:str
    activeMembers:int

class Receipt(BaseModel):
    requestId:str
    movement:int | None
    status:Literal["pending","completed","not_found","conflict"]

class Health(BaseModel):
    status:Literal["UP"]
    legacy:Literal["UP","DOWN"]

class Migration(BaseModel):
    domains:dict[str,Literal["LEGACY","DUAL","MODERN"]]

class Error(BaseModel):
    message:str
    error_id:str
    code:str | None=None
