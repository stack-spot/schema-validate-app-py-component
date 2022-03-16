from dataclasses import dataclass


@dataclass(frozen=True)
class EventModel:
    __slots__ = ['event_id', 'event_time', 'data_product', 'schema_name', 'schema_version', 'event_data']
    event_id: str
    event_time: str
    data_product: str
    schema_name: str
    schema_version: str
    event_data: dict



