from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    def __init_subclass__(cls, **kwargs):
    
        cls.__tablename__ = cls.__name__.lower()
        super().__init_subclass__(**kwargs)

    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


    def __repr__(self):
        return f"<{self.__class__.__name__}({self.to_dict()})>"
