#!/usr/bin/env python3
"""Auth module"""
import uuid
from sqlalchemy.orm.exc import NoResultFound
from user import User
import bcrypt
from db import DB


def _hash_password(password: str) -> bytes:
    """Return a salted hash of the input password"""
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash


def _generate_uuid() -> str:
    """Return a new unique identifier"""
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database."""

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Return the newly registered user"""
        if (
            email is None
            or not isinstance(email, str)
            or password is None
            or not isinstance(password, str)
        ):
            raise ValueError("email or password is missing")

        try:
            user = self._db.find_user_by(email=email)
            raise ValueError("User {} already exists".format(user.email))
        except NoResultFound:
            hashed = _hash_password(password)
            return self._db.add_user(email=email, hashed_password=hashed)

    def valid_login(self, email: str, password: str) -> bool:
        """Check if login details are valid"""
        try:
            user = self._db.find_user_by(email=email)
            pass_bytes = password.encode("utf-8")
            return bcrypt.checkpw(pass_bytes, user.hashed_password)
        except Exception:
            return False

    def create_session(self, email: str) -> str:
        """Return session ID"""
        try:
            user = self._db.find_user_by(email=email)
            user.session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=user.session_id)
            return user.session_id
        except Exception:
            return None

    def get_user_from_session_id(self, session_id: str) -> User | None:
        """Return user that has a session id"""
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except Exception:
            return None

    def destroy_session(self, user_id: str) -> None:
        """Updates the corresponding user’s session ID to `None`"""
        self._db.update_user(user_id, session_id=None)
        return None

    def get_reset_password_token(self, email: str) -> str:
        """Generate reset password token"""
        try:
            user = self._db.find_user_by(email=email)
            uuid = _generate_uuid()
            self._db.update_user(user.id, reset_token=uuid)
            return uuid
        except NoResultFound:
            raise ValueError("Email not found")

    def update_password(self, reset_token: str, password: str) -> None:
        """Update password"""
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed = _hash_password(password)
            self._db.update_user(
                user.id, hashed_password=hashed, reset_token=None
            )
        except NoResultFound:
            raise ValueError("Invalid reset token")
