import pydantic
import pydantic.alias_generators


class Position(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True)

    column: int
    line_number: int


class Range(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True)

    end_column: int
    end_line_number: int
    start_column: int
    start_line_number: int


class Change(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True)

    range: Range
    range_length: int
    range_offset: int
    text: str
