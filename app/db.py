from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData, CheckConstraint


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(20), nullable=False)

    expenses: Mapped[list["Expenses"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint("length(username) > 4", name="username_min_length"),
        CheckConstraint("length(password) > 4", name="password_min_length"),
    )

    def __repr__(self) -> str:
        return f"<User {self.id} {self.username}>"


class Expenses(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(50))
    amount: Mapped[float] = mapped_column(db.DECIMAL(precision=5, scale=2))
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="expenses")

    def __repr__(self) -> str:
        return f"<{self.id} - {self.title}>"
