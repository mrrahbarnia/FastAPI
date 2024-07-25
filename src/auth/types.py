from typing import NewType
from uuid import UUID

UserId = NewType("UserId", int)
ProfileId = NewType("ProfileId", UUID)
Email = NewType("Email", str)
Password = NewType("Password", str)
