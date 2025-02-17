from flask_jwt_extended import JWTManager

from app.db import db, User

jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_lookup(user_id: int) -> id:
    return user_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: dict, jwt_data: dict) -> User | None:
    identity = jwt_data.get("sub")
    return db.session.query(User).filter(User.id == identity).one_or_none()
