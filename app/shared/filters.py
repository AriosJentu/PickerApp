from typing import Any, Callable, Optional
from sqlalchemy.sql.expression import ColumnElement


type Operator = Callable[[ColumnElement, Any], Optional[ColumnElement]]


class FilterField:


    def __init__(
        self,
        field_type: type,
        default: Any = None,
        operator: Operator = None
    ):
        
        if operator is None:
            operator = self.exact
            if field_type == str:
                operator = self.like

        self.field_type = field_type
        self.default = default
        self.operator = operator


    def apply_filter(self, column: ColumnElement, value: Any) -> Optional[ColumnElement]:
        return self.operator(column, value)


    @staticmethod
    def empty(column: ColumnElement, value: Any) -> None:
        return None
    

    @staticmethod
    def exact(column: ColumnElement, value: Any) -> ColumnElement:
        return column == value


    @staticmethod
    def like(column: ColumnElement, value: str) -> ColumnElement:
        return column.ilike(f"%{value}%")


    @staticmethod
    def gte(column: ColumnElement, value: Any) -> ColumnElement:
        return column >= value


    @staticmethod
    def lte(column: ColumnElement, value: Any) -> ColumnElement:
        return column <= value


    @staticmethod
    def gt(column: ColumnElement, value: Any) -> ColumnElement:
        return column > value


    @staticmethod
    def lt(column: ColumnElement, value: Any) -> ColumnElement:
        return column < value


    @staticmethod
    def ne(column: ColumnElement, value: Any) -> ColumnElement:
        return column != value


    @staticmethod
    def in_list(column: ColumnElement, values: list[Any] | Any) -> ColumnElement:
        return column.in_(values) if isinstance(values, list) else column == values
