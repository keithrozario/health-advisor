import boto3
import pprint
import json

Session_Local = boto3.session.Session(profile_name='nnatri+testenv-unicorngymrole', region_name="us-east-1")
bedrock_agent_runtime_client = Session_Local.client('bedrock-agent-runtime')

def getAnswers(questions):
    knowledgeBaseResponse  = bedrockClient.retrieve_and_generate(
        input={'text': questions},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': 'WCORHJLNTQ',
                'modelArn': 'arn:aws:bedrock:us-east-1:205079877575:inference-profile/us.anthropic.claude-3-5-haiku-20241022-v1:0'
            },
            'type': 'KNOWLEDGE_BASE'
        })
    return knowledgeBaseResponse

# questions = "What is my HIV results?"
# response = getAnswers(questions)
# print(response['output']['text'])





try:
    agent_response = bedrock_agent_runtime_client.invoke_agent(
        inputText="What is my HIV results",
        agentId="WCORHJLNTQ",
        agentAliasId="ODRJYJEDVX",
        sessionId="12345",
    )
    pprint.pprint(agent_response)
    if 'completion' not in agent_response:
        raise ValueError("Missing 'completion' in agent response")
    for event in agent_response['completion']:
        chunk = event.get('chunk')
        print('chunk: ', chunk)
        if chunk:
            decoded_bytes = chunk.get("bytes").decode()
            print('bytes: ', decoded_bytes)
            if decoded_bytes.strip():
                message = json.loads(decoded_bytes)
                if message['type'] == "content_block_delta":
                    print(message['delta']['text']) or ""
                elif message['type'] == "message_stop":
                    print("\n")
except Exception as e:
    print(e)