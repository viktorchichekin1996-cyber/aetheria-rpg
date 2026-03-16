from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Combat(Base):
    __tablename__ = "combats"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, nullable=False)
    player2_id = Column(Integer, nullable=False)
    player1_hp = Column(Integer, default=100)
    player2_hp = Column(Integer, default=100)
    turn = Column(Integer, default=1)
    log = Column(JSONB, default=[])
    winner_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, default=func.now())
    ended_at = Column(TIMESTAMP, nullable=True)