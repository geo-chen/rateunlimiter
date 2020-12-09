import boto3


class IPManager():
    def __init__(self, access_key, secret_key, region):
        self.api_ids = []
        self.endpoints = []
        self.region = region
        self.awsclient = boto3.client("apigatewayv2", aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

    def create(self, dest_url):
        """Creates a single API gateway with HTTP proxy integration for endpoint dest_url"""
        create_api_response = self.awsclient.create_api(
            Name="rateapi",
            ProtocolType="HTTP"
        )
        create_route_response = self.awsclient.create_route(
            ApiId=create_api_response['ApiId'],
            AuthorizationType="NONE",
            RouteKey="$default"
        )
        create_stage_response = self.awsclient.create_stage(
            ApiId=create_api_response['ApiId'],
            StageName="$default"
        )
        create_integration_response = self.awsclient.create_integration(
            ApiId=create_api_response['ApiId'],
            IntegrationMethod="ANY",
            IntegrationType="HTTP_PROXY",
            IntegrationUri=dest_url
        )
        create_deployment_response = self.awsclient.create_deployment(
            ApiId=create_api_response['ApiId'],
            StageName="$default"
        )
        self.api_ids.append(create_api_response['ApiId'])
        self.endpoints.append(f"{create_api_response['ApiId']}.execute-api.{self.region}.amazonaws.com")

    def clear(self):
        """Removes all API endpoints."""
        for api in self.api_ids:
            self.awsclient.delete_api(ApiId=api)