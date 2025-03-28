from typing import Any, Callable, Optional

from sqlalchemy.sql.expression import ColumnElement


type Operator = Callable[[ColumnElement, Any], Optional[ColumnElement]]

class FilterField:


    def __init__(
        self,
        field_type: type,
        default: Optional[Any] = None,
        operator: Optional[Operator] = None,
        dependency: Optional[str] = None,
        ignore: Optional[bool] = False
    ):
        
        if operator is None:
            operator = self.exact
            if field_type == str:
                operator = self.like

        self.field_type = field_type
        self.default = default
        self.operator = operator
        self.dependency = dependency
        self.ignore = ignore


    def apply_filter(self, column: ColumnElement, value: Any) -> Optional[ColumnElement]:
        if not self.ignore:
            return self.operator(column, value)
        return None
    
    
    def is_dependent(self) -> bool:
        return (self.dependency is not None)
    

    @staticmethod
    def exact(column: ColumnElement, value: Any) -> ColumnElement:
        return column == value


    @staticmethod
    def like(column: ColumnElement, value: str) -> ColumnElement:
        return column.ilike(f"%{value}%")
