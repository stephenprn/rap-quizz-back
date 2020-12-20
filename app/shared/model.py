from sqlalchemy import inspect
import enum

from app.utils.utils_string import generate_uuid
from app.shared.db import db


class ModelType(enum.Enum):
    BASE = "BASE"
    ASSOCIATION = "ASSOCIATION"


class ModelCommon(db.Model):
    __abstract__ = True

    def __repr__(self):
        state = inspect(self)

        def ga(attr):
            return (
                repr(getattr(self, attr))
                if attr not in state.unloaded
                else "<deferred>"
            )

        attrs = " ".join([f"{attr.key}={ga(attr.key)}" for attr in state.attrs])
        return f"<{self.__tablename__} {attrs}>"

    def to_dict(self):
        state = inspect(self)

        # load of non-relationship properties
        # add property to dict only if column is loaded (can be excluded with load_only)

        res = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if not c.primary_key and c.name not in state.unloaded
        }

        # load of relationship propeties
        for rel in state.mapper.relationships:
            key = rel.key

            if key not in state.unloaded:
                value = getattr(self, key)

                if isinstance(value, list):
                    res[key] = [elt.to_dict() for elt in value]
                else:
                    res[key] = value.to_dict()

        return res


class ModelAssociation(ModelCommon):
    __abstract__ = True
    model_type = ModelType.ASSOCIATION


class ModelBase(ModelCommon):
    __abstract__ = True
    model_type = ModelType.BASE

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, default=generate_uuid, unique=True, nullable=False)

    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    update_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
