import os
import openai
from dotenv import load_dotenv
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

load_dotenv(override=True)
phoenix_host = os.getenv('ARIZE_PHOENIX_HOST')
phoenix_port = os.getenv('ARIZE_PHOENIX_PORT')
tracer_provider = register(
    project_name="playground-basic-tracing",
    endpoint=f'{phoenix_host}:{phoenix_port}/v1/traces',
)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
client = openai.OpenAI(
    base_url=os.getenv('LM_STUDIO_HOST'),
    api_key=os.getenv('LM_STUDIO_API_KEY')
)


def main():
    response = client.chat.completions.create(
        model=os.getenv('LM_STUDIO_MODEL_ID', ''),
        messages=[{
            "role": "user",
            "content": "Sally has 3 brothers. Each of her brothers has 2 sisters. How many sisters does Sally have?"
        }]
    )
    print(response.choices[-1].message.content)


if __name__ == "__main__":
    main()
