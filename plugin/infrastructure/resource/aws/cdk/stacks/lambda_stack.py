from .helpers.file import get_policy, get_role
from plugin.utils.file import interpolate_json_template
from plugin.utils.string import kebab

from aws_cdk import core as cdk
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam


class Lambda(cdk.Stack):
    """
    TO DO
    Args:
        cdk ([type]): [description]
    """

    def create_dynamo_table(self, registry: str, flavor: dict) -> dynamodb.CfnTable:
        cfn_table = dynamodb.CfnTable(self, f"dynamo-table-{registry}",
                                      key_schema=[dynamodb.CfnTable.KeySchemaProperty(
                                          attribute_name="Schema",
                                          key_type="HASH"
                                      ), dynamodb.CfnTable.KeySchemaProperty(
                                          attribute_name="VersionNumber",
                                          key_type="RANGE"
                                      )],
                                      attribute_definitions=[dynamodb.CfnTable.AttributeDefinitionProperty(
                                          attribute_name="Schema",
                                          attribute_type="S"
                                      ), dynamodb.CfnTable.AttributeDefinitionProperty(
                                          attribute_name="VersionNumber",
                                          attribute_type="N"
                                      )],
                                      provisioned_throughput=dynamodb.CfnTable.ProvisionedThroughputProperty(
                                          read_capacity_units=flavor["dynamo"]["read"]["maximum"],
                                          write_capacity_units=flavor["dynamo"]["write"]["maximum"]
                                      ),
                                      table_class="STANDARD",
                                      table_name=registry
                                      )
        return cfn_table

    def create_lambda_layer(self, name: str, lambda_name: str, key: str, description: str = '') -> lambda_.CfnLayerVersion:
        cfn_layer_version = lambda_.CfnLayerVersion(self, f"lambda-layer-{name}",
                                                    content=lambda_.CfnLayerVersion.ContentProperty(
                                                        s3_bucket=f'{self.account}-{kebab(lambda_name)}-gateway-assets',
                                                        s3_key=key,
                                                    ),
                                                    compatible_architectures=["x86_64"],
                                                    compatible_runtimes=["python3.9"],
                                                    description=description,
                                                    layer_name=name
                                                    )
        return cfn_layer_version

    def create_lambda_for_schema_validation(self, name: str, registry: str,  region: str, flavor: dict):
        cfn_avro_layer = self.create_lambda_layer(f'avro_layer_{name}', name, 'avro_layer.zip')
        cfn_xray_layer = self.create_lambda_layer(f'xray_layer_{name}', name, 'xray_layer.zip')
        role = iam.CfnRole(
            self,
            f'{name}-api-lambda-role',
            role_name=f'{kebab(name)}-api-lambda-role',
            assume_role_policy_document=get_role("OsDataRoleLambda"),
            policies=[iam.CfnRole.PolicyProperty(
                policy_document=interpolate_json_template(
                    get_policy("OsDataPolicyLambdaRegistry"),
                    {
                        "AwsAccount": self.account,
                        "AwsRegion": region,
                        "RegistryNameDB":registry,
                        "RegistryName": kebab(registry)
                    }
                ),
                policy_name=f'{kebab(name)}-api-lambda-policy'
            )]
        )

        lambda_function_name = f'{kebab(name)}-api-lambda-schema'
        bucket = s3.Bucket.from_bucket_arn(
            self,
            f'import-{name}-bucket-assets',
            f'arn:aws:s3:::{self.account}-{kebab(name)}-gateway-assets'
        )

        lambda_fn = lambda_.CfnFunction(
            self,
            lambda_function_name,
            code=lambda_.CfnFunction.CodeProperty(
                s3_bucket=bucket.bucket_name,
                s3_key=f'{kebab(name)}-api-lambda.zip'
            ),
            description="Lambda function used for data schema validation",
            function_name=lambda_function_name,
            handler="main.main",
            runtime="python3.8",
            memory_size=flavor["function"]["memory"],
            timeout=flavor["function"]["time-limit"],
            layers=[cdk.Fn.ref(cfn_avro_layer.logical_id), 
                    cdk.Fn.ref(cfn_xray_layer.logical_id)],
            role=role.attr_arn,
            tags=[cdk.CfnTag(
                key="name",
                value=lambda_function_name
            )],
            tracing_config=lambda_.CfnFunction.TracingConfigProperty(
                mode="Active"
            )

        )
        lambda_fn.add_depends_on(role)
        lambda_fn.add_depends_on(cfn_xray_layer)
        lambda_fn.add_depends_on(cfn_avro_layer)
        return lambda_fn

    def create_bucket_for_lambda_assets(self, name: str):
        return s3.Bucket(
            self,
            id=kebab(f'dp-{name}'),
            bucket_name=kebab(name),
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=False
        )
