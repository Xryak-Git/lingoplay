from typing import Annotated

from pydantic import Field

PrimaryKey = Annotated[int, Field(gt=0, lt=2147483647)]
