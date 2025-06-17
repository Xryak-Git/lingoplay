

from pydantic import Field

from typing import Annotated


PrimaryKey = Annotated[int, Field(gt=0, lt=2147483647)]