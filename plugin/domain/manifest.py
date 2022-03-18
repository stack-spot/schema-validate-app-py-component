from __future__ import annotations
from dataclasses import dataclass
from plugin.utils.file import read_yaml
from .validation import ValidationManifest as val_


@dataclass
class SchemaValidate:
    """
    TO DO
    """

    name: str
    region: str
    registry: str
    type: str
    api_name: str

    def __post_init__(self):
        val_.checking_vars_type(
                self, name='str', region='str', type='str', registry='str', api_name='str')
        val_.checking_the_type(self)


@dataclass
class Manifest:
    """
    TO DO
    """

    schema_validate: SchemaValidate

    def __init__(self, manifest) -> None:
        if isinstance(manifest, str):
            file = read_yaml(manifest)
            self.schema_validate = SchemaValidate(**file['schema_validate'])
        elif isinstance(manifest, dict):
            self.schema_validate = SchemaValidate(**manifest['schema_validate'])
        else:
            raise TypeError
