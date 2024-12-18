import boto3
import pprint
import json
import botocore

Session_Local = boto3.session.Session(profile_name='nnatri+testenv-unicorngymrole', region_name="us-east-1")
bedrock_agent_runtime_client = Session_Local.client('bedrock-agent-runtime')
agent_id = "WCORHJLNTQ"
agentAliasId = "ODRJYJEDVX"

def getAnswers(questions):
    knowledgeBaseResponse  = bedrock_agent_runtime_client.retrieve_and_generate(
        input={'text': questions},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': 'WCORHJLNTQ',
                'modelArn': 'arn:aws:bedrock:us-east-1:205079877575:inference-profile/us.anthropic.claude-3-5-haiku-20241022-v1:0'
            },
            'type': 'KNOWLEDGE_BASE'
        })
    return knowledgeBaseResponse

def get_agent_response(question: str, session_id: str) -> str:
    
    agent_response = bedrock_agent_runtime_client.invoke_agent(
        inputText=question,
        agentId=agent_id,
        agentAliasId=agentAliasId,
        sessionId=session_id,
    )
    responses = []
    
    try:
        for event in agent_response['completion']:
            chunk = event.get('chunk')
            if chunk:
                responses.append(chunk.get("bytes").decode())
    except botocore.exceptions.EventStreamError as e:
        return "Throttling Error: Please stop asking me so many questions"

    return "\n".join(responses)