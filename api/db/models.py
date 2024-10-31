from api.db.database import Base
from sqlalchemy import Column, func, Enum, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from api.enums.task import TaskStatus, PriorityLevel
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4) # change to UUID
    email = Column(String, nullable=False, unique=True)
    username = Column(String)
    password = Column(String)
    tasks = relationship("Task", back_populates="user")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    dueDate = Column(Date, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # Optional Attributes
    priority = Column(Enum(PriorityLevel), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    user = relationship("User", back_populates="tasks")
