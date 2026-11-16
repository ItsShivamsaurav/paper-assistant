from sqlalchemy import select

from app.auth.models import User
from app.auth.security import hash_password
from app.database.connection import Base, SessionLocal, engine


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_default_user(
    username: str = "shivam",
    password: str = "shivam",
    email: str = "shivam@example.com",
) -> User | None:
    db = SessionLocal()
    try:
        existing_user = db.scalar(
            select(User).where(User.username == username)
        )

        if existing_user:
            return existing_user

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="user",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_default_user()
    print("Database initialized successfully.")