from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    tg_id = Column(Integer, primary_key=True)
    tpu_id = Column(String, nullable=False, unique=False)

    directories = relationship("Directory", back_populates="user", cascade="all, delete")

    def __str__(self):
        return str(self.tg_id)

    def __repr__(self):
        return str(self)

class Directory(Base):
    __tablename__ = "directories"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, ForeignKey("user.tg_id"))
    directory = Column(String, nullable=False)

    user = relationship("User", back_populates="directories")

    def __str__(self):
        return f"{self.user_id} - {self.directy}"
