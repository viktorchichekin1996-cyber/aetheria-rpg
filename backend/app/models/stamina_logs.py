from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from app.database import Base


class StaminaLog(Base):
    __tablename__ = "stamina_logs"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, ForeignKey("users.vk_id", ondelete="CASCADE"), index=True)
    action = Column(String(50), nullable=False)
    stamina_change = Column(Integer, nullable=False)
    stamina_before = Column(Integer, nullable=False)
    stamina_after = Column(Integer, nullable=False)
    warning_triggered = Column(String(10), nullable=True)
    location = Column(String(50), default='unknown')
    timestamp = Column(TIMESTAMP, default=func.now(), index=True)