import click
from plugin.usecase.schemavalidate.main import DataSchemaValidateUseCase
from plugin.infrastructure.resource.aws.cdk.main import AwsCdk
from plugin.domain.manifest import Manifest


@click.group()
def apply():
    pass # We just need a click.group to create our command


@apply.command('data-schema-validation')
@click.option('-f', '--file', 'path')
def apply_lambda_validate(path: str):
    manifest = Manifest(manifest=path)
    DataSchemaValidateUseCase(AwsCdk()).apply(manifest.schema_validate)
