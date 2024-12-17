from aws_cdk import (
    Aws,
    Duration,
    Stack,
    aws_lambda,
    aws_kms,
    aws_iam,
)
from constructs import Construct
from aws_cdk import aws_dynamodb as dynamodb

class DynamoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Some externals layer we need
        powertools_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            id="PowertoolsLayer",
            layer_version_arn=f"arn:aws:lambda:{Aws.REGION}:017000801446:layer:AWSLambdaPowertoolsPythonV2:69",
        )
        pytz_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            id="PytzLayer",
            layer_version_arn=f"arn:aws:lambda:{Aws.REGION}:770693421928:layer:Klayers-p312-pytz:1",
        ) 

        table_key = aws_kms.Key(self, 
            "UnicornGymDynamoKey",
            key_spec = aws_kms.KeySpec.SYMMETRIC_DEFAULT
        )

        # Tablev2 in the docs refers to global tables, and table (without V2) is the normal tables
        table = dynamodb.Table(self,
            "CalendarsTable",
            table_name="Calendars",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=table_key,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # History index
        history_index_name = "PatientHistory"
        table.add_global_secondary_index(
            index_name=history_index_name,
            partition_key=dynamodb.Attribute(name="patient", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING)
        )

        environment = {
            "TABLE_NAME": table.table_name
        }

        booking_function = aws_lambda.Function(
            self,
            "BookingFn",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            function_name="booking",
            layers=[powertools_layer, pytz_layer],
            code=aws_lambda.Code.from_asset("lambda_functions"),
            handler="booking.main",
            environment=environment,
            memory_size=512,
            timeout=Duration.seconds(29),
        )
        booking_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                        "dynamodb:BatchWriteItem",
                        "dynamodb:PutItem",
                        "dynamodb:Query"],
                resources=[table.table_arn],
            )
        )
        table_key.grant_encrypt_decrypt(
            booking_function.grant_principal       
        )

        history_function = aws_lambda.Function(
            self,
            "HistoryFn",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            layers=[powertools_layer],
            code=aws_lambda.Code.from_asset("lambda_functions"),
            function_name="history",
            handler="history.main",
            environment=environment,
            memory_size=512,
            timeout=Duration.seconds(29),
        )
        history_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["dynamodb:Query"],
                resources=[f"{table.table_arn}/index/{history_index_name}"],
            )
        )
        table_key.grant_encrypt_decrypt(
            history_function.grant_principal       
        )
