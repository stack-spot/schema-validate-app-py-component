from .stacks import Stack
from .engine.main import CDKEngine
from plugin.utils.logging import logger
from plugin.domain.manifest import SchemaValidate
from plugin.infrastructure.resource.aws.services.main import SDK
from plugin.utils.string import kebab
from plugin.infrastructure.resource.interface import DataSchemaValidateCloudInterface


class AwsCdk(CDKEngine, DataSchemaValidateCloudInterface):
    """
    TODO
    """
    def create_assets(self, schema_validate: SchemaValidate):
        self.new_app()
        cloud_service = SDK()
        name = f"{cloud_service.account_id}-{schema_validate.name}-gateway"
        stack_name = f'create-{name}-assets'.replace('_', '-')
        stack = Stack(self.app, stack_name)

        bucket_logs_exist = cloud_service.check_bucket(f'{kebab(name)}-logs')
        bucket_assets_exist = cloud_service.check_bucket(
            f'{kebab(name)}-assets')

        if not bucket_logs_exist:
            stack.create_bucket_for_lambda_assets(f'{kebab(name)}-logs')
        else:
            logger.info("Bucket %s-logs already exists.", kebab(name))

        if not bucket_assets_exist:
            stack.create_bucket_for_lambda_assets(f'{kebab(name)}-assets')
        else:
            logger.info("Bucket %s-assets already exists.", kebab(name))

        if not bucket_logs_exist or not bucket_assets_exist:
            self.deploy(stack_name, schema_validate.region)


    def create_function(self, name: str, registry: str, region: str, flavor: dict):
        self.new_app()
        stack_name = f'create-{name}-api-functions'.replace('_', '-')
        stack = Stack(self.app, stack_name)
        stack.create_dynamo_table(registry, flavor)
        stack.create_lambda_for_schema_validation(name, registry,  region, flavor)
        self.deploy(stack_name, region)


    def create_api_resource(self, schema_validate: SchemaValidate, resource: dict):
        self.new_app()
        stack_name = f'apply-{schema_validate.name}-api-validation'.replace('_', '-')
        stack = Stack(self.app, stack_name)
        stack.create_api_resource(schema_validate, resource)
        self.deploy(stack_name, schema_validate.region)
