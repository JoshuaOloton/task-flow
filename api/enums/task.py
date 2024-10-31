import enum

class TaskStatus(str, enum.Enum):
    pending = "pending"
    inprogress = "in-progress"
    completed = "completed"

class PriorityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"