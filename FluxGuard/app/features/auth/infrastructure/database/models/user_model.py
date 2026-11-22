from sqlalchemy import Integer,ForeignKey,Boolean,DateTime,String,Uuid
from uuid import UUID
from sqlalchemy.orm import Mapped,mapped_column
from app.core.infrastructure.database.database import Base
from app.features.auth.domain.entities.user import UserRole
from datetime import datetime,timezone

class UserModel(Base):
    __tablename__ = "users"

    id : Mapped[UUID] = mapped_column(Uuid,primary_key=True)
    fullname : Mapped[str] = mapped_column(String(50),nullable=False)
    email : Mapped[str] = mapped_column(String(50),index=True,unique=True)
    role : Mapped[UserRole] = mapped_column(String(50))
    is_active : Mapped[bool] = mapped_column(Boolean,default=True)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc))