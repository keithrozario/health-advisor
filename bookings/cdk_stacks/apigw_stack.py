from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda
from constructs import Construct


class ApiGWStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = apigateway.LambdaRestApi(
            self,
            "HealthApi",
            handler=aws_lambda.Function.from_function_name(
                self, "defaultFunction", "booking"
            ),
            proxy=False,
        )

        # Define the '/booking' resource with a POST method
        booking_handler =aws_lambda.Function.from_function_name(
                self, "bookingFunction", "booking"
        )
        booking_resource = api.root.add_resource("booking")
        booking_resource.add_method("POST", apigateway.LambdaIntegration(booking_handler))

        # Define the '/history' resource with a GET method
        history_handler =aws_lambda.Function.from_function_name(
                self, "historyFunction", "history"
        )
        history_resource = api.root.add_resource("history")
        history_resource.add_method("GET", apigateway.LambdaIntegration(history_handler))
