from .connection import Base, engine
from . import models


def init_database():
    Base.metadata.create_all(bind=engine)
    print("AeroMind database initialized successfully.")


if __name__ == "__main__":
    init_database()