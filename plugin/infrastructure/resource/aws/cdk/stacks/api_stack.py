from aws_cdk import core as cdk
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam
from .helpers.file import get_role, get_policy
from plugin.utils.string import kebab
from plugin.domain.manifest import SchemaValidate


class ApiGateway(cdk.Stack):
    """
    TO DO
    Args:
        cdk ([type]): [description]
    """

    def create_api_resource(self, schema_validate: SchemaValidate, resource: dict):

        iam.CfnRole(
            self,
            f"{schema_validate.name}-role-api-gateway-role",
            role_name=kebab(f"{schema_validate.name}-role-api-gateway"),
            assume_role_policy_document=get_role("OsDataRoleApi"),
            policies=[
                iam.CfnRole.PolicyProperty(
                    policy_document=get_policy("OsDataPolicyApi"),
                    policy_name=kebab(f"{schema_validate.name}-api-lambda-policy")
                )
            ]
        )

        uri_arn = f'2015-03-31/functions/arn:aws:lambda:{schema_validate.region}:{cdk.Stack.of(self).account}:function:{kebab(f"{schema_validate.name}-api-lambda-schema")}/invocations'
        api = apigateway.RestApi.from_rest_api_attributes(
            self,
            "import-rest-api",
            rest_api_id=schema_validate.api_id,
            root_resource_id=resource["id"]
        )

        res = api.root.add_resource("stack-analytics").add_resource("schema-validation").add_resource(
            "v1.0.0") if resource["path"] == "/" else api.root.add_resource("schema-validation").add_resource("v1.0.0")

        full_res = res.add_resource("events")\
            .add_resource("{datalake_name}")\
            .add_resource("{schema_version}")\
            .add_resource("{schema_name}")

        role = iam.Role.from_role_arn(
            self,
            "import-role-api",
            role_arn=f'arn:aws:iam::{cdk.Stack.of(self).account}:role/{kebab(schema_validate.name)}-role-api-gateway')

        
        full_res.add_method(
            "POST",
            apigateway.AwsIntegration(
                service="lambda",
                path=uri_arn,
                region=schema_validate.region,
                proxy=True,
                options=apigateway.IntegrationOptions(
                        credentials_role=role,
                        timeout=cdk.Duration.seconds(10)
                )
            ),
            method_responses=[apigateway.MethodResponse(status_code="200")],
            authorization_type=apigateway.AuthorizationType.IAM,
            api_key_required=True
        )
