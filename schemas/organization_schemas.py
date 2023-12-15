from pydantic import BaseModel
from typing import List

class OrgBase(BaseModel):
    org_name: str

class OrgCreate(OrgBase):
    pass

class OrgUpdate(OrgBase):
    pass

class OrgRead(OrgBase):
    id: int

    class Config:
        from_attributes = True