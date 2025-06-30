from typing import Annotated

from sqlalchemy.orm import mapped_column

PrimaryKey = Annotated[int, mapped_column(primary_key=True)]
