#!/usr/bin/env python3
"""DB module
"""
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User


class DB:
    """DB class"""

    def __init__(self) -> None:
        """Initialize a new DB instance"""
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object"""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Save the user to the database
        Returns:
            User: A user object
        """
        user = User(email=email, hashed_password=hashed_password)

        self._session.add(user)
        self._session.commit()

        return user

    def find_user_by(self, **kwargs: Any) -> User:
        """Find user
        Takes in arbitrary keyword arguments and returns the first row found
        in the users table as filtered by the method’s input arguments.
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if not user:
                raise NoResultFound
            return user
        except InvalidRequestError as e:
            raise e

    def update_user(self, user_id: int, **kwargs: Any) -> None:
        """Update user's attributes passed as arguments"""
        user = self.find_user_by(id=user_id)

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise ValueError(
                    "{} does not correspond to a user attribute".format(key)
                )

        self._session.commit()
