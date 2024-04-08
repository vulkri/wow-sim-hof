from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True)
    char_name = Column(String, unique=True, index=True)
    item_level = Column(Integer)
    last_sim = Column(DateTime)
    dps = Column(Integer)