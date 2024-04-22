from sqlalchemy import Column, DateTime, Integer, String


from database import Base

# Leaderboard entry saved after quick sim
class LeaderboardEntry(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True)
    char_name = Column(String, index=True)
    char_class = Column(String)
    specialization_id = Column(Integer, index=True)
    specialization_name = Column(String)
    last_sim = Column(DateTime)
    dps = Column(Integer)
    item_level = Column(Integer)