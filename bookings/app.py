#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_stacks.dynamodb_stack import DynamoStack
from cdk_stacks.apigw_stack import ApiGWStack

env = cdk.Environment(region="")

app = cdk.App()
dynamo_stack = DynamoStack(app, "DynamoStack", env=env)
apigw_stack = ApiGWStack(app, "ApiGWStack", env=env)
apigw_stack.add_dependency(dynamo_stack)
app.synth()