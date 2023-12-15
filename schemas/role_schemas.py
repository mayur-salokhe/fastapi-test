from pydantic import BaseModel
from typing import List

class RoleBase(BaseModel):
	org_id: int
	user_id: int
	role: str

class RoleCreate(RoleBase):
	pass

class RoleUpdate(RoleBase):
	pass

class RoleRead(RoleBase):
	id: int
	
	class Config:
		from_attributes = True