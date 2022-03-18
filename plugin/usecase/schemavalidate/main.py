from plugin.infrastructure.resource.interface import DataSchemaValidateCloudInterface
from plugin.usecase.schemavalidate.interface import DataSchemaValidateInterface
from plugin.infrastructure.resource.aws.services.main import SDK
from plugin.utils.file import create_lambda_package, get_current_pwd, remove_from_os, read_yaml
from plugin.utils.string import kebab
from plugin.domain.manifest import SchemaValidate


class DataSchemaValidateUseCase(DataSchemaValidateInterface):
    """
    TODO
    """
    cloud: DataSchemaValidateCloudInterface

    def __init__(self, cloud: DataSchemaValidateCloudInterface) -> None:
        self.cloud = cloud

    def __upload_object_cloud(self, schema_validate: SchemaValidate, cloud_service: SDK) -> None:

        lambda_zip_file =  f'{kebab(schema_validate.name)}-api-lambda.zip'
        create_lambda_package("src/schema_validation", lambda_zip_file)
        bucket_name = kebab(
            f'{cloud_service.account_id}-{schema_validate.name}-gateway-assets')
        cloud_service.upload_object(f'{get_current_pwd()}/{lambda_zip_file}',
                                    bucket_name, lambda_zip_file)
        cloud_service.upload_object(f'{get_current_pwd()}/src/layers/avro/avro_layer.zip',
                                    bucket_name, "avro_layer.zip")
        cloud_service.upload_object(f'{get_current_pwd()}/src/layers/xray/xray_layer.zip',
                                    bucket_name, "xray_layer.zip")

        remove_from_os(
            f'{get_current_pwd()}/{lambda_zip_file}')

    def __read_flavors(self, type: str) -> dict:
        flavors = read_yaml(
            'plugin/usecase/schemavalidate/flavors/function.yml')
        return flavors["flavors"][type]

    def apply(self, schema_validate: SchemaValidate) -> bool:
        cloud_service = SDK()
        self.cloud.create_assets(schema_validate)
        self.__upload_object_cloud(schema_validate, cloud_service)
        flavor = self.__read_flavors(schema_validate.type)
        if cloud_service.not_exists_lambda(f"{schema_validate.name}-api-lambda-schema", schema_validate.region):
            self.cloud.create_function(
                schema_validate.name, schema_validate.registry, schema_validate.region, flavor)

        resource = cloud_service.get_api_resource_id(
            schema_validate.api_name, "stack-analytics", schema_validate.region)
        self.cloud.create_api_resource(schema_validate, resource)

        return True
