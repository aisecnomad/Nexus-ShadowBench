import boto3
client = boto3.client('bedrock-runtime')
client.invoke_model(modelId='anthropic.claude-3-haiku')
