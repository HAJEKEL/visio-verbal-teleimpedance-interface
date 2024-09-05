from functions.openai_version import import_openai_version

import_openai_version('/app/openai_latest')
from decouple import config

organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")

client = openai_latest.OpenAI(api_key=api_key, organization=organization)