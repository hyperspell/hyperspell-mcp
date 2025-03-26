from dataclasses import dataclass
from typing import Self, Sequence, overload

from pydantic import BaseModel as PydanticBaseModel


@dataclass
class BaseModel:
    @overload
    @classmethod
    def from_pydantic(cls, model: PydanticBaseModel) -> Self: ...

    @overload
    @classmethod
    def from_pydantic(cls, model: Sequence[PydanticBaseModel]) -> list[Self]: ...

    @classmethod
    def from_pydantic(
        cls, model: PydanticBaseModel | Sequence[PydanticBaseModel]
    ) -> Self | list[Self]:
        """Convert a Pydantic model to a data class, selecting only the keys that are part of the data class."""
        if isinstance(model, Sequence):
            return [cls.from_pydantic(m) for m in model]

        data = model.model_dump()
        # Only select the keys in data that are part of this data class
        data = {key: value for key, value in data.items() if key in cls.__annotations__}
        return cls(**data)


@dataclass
class Collection(BaseModel):
    name: str
    documents_count: int = 0


@dataclass
class Document(BaseModel):
    id: int
    title: str
    type: str
    summary: str
