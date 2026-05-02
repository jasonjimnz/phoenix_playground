import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

load_dotenv(override=True)
phoenix_host = os.getenv('ARIZE_PHOENIX_HOST')
phoenix_port = os.getenv('ARIZE_PHOENIX_PORT')
tracer_provider = register(
    project_name="playground-basic-agent",
    endpoint=f'{phoenix_host}:{phoenix_port}/v1/traces',
)
tracer = tracer_provider.get_tracer(__name__)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)


@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    return str(eval(expression))


model = ChatOpenAI(
    base_url=os.getenv('LM_STUDIO_HOST'),
    api_key=os.getenv('LM_STUDIO_API_KEY'),
    model=os.getenv('LM_STUDIO_MODEL_ID', '')
)
agent = create_agent(
    model=model,
    tools=[calculate]
)
queries = [
    "What is (250 / (5 * 2)) + (14 * 3)?",
    "Calculate 1000 - (15 ** 2) / 5",
    "What is 3.14159 * (12.5 / 0.5)",
    "What is the result of 1 / 7 rounded to 4 decimal places?",
    "What is 1,234,567 multiplied by 8,910?",
    "Calculate 2 to the power of 20",
    "What do I get if I divide the square of 12 by the sum of 3 and 5?",
    "Subtract 45 from the product of 12 and 12",
    "Take 100, add 25 percent, then divide by 5",
    "What is the remainder of 145 divided by 12?",
    "What is 500 integer divided by 7?",
    "Is 2 ** 10 greater than 1000?",
    "Determine if (15 * 3) is equal to (9 * 5)",
    "What is ((12 * 4) / (2 ** 3)) + (144 ** 0.5 * 2) - 5",
    "Calculate the value of (100 * 1.05 ** 10) for compound interest"
]


@tracer.agent(name="calculation-agent")
def call_agent(query: str) -> str:
    response = agent.invoke({"messages": [("user", query)]})
    return response['messages'][-1].content


@tracer.chain(name="basic-agent")
def main():
    for query in queries:
        call_agent(query)


if __name__ == "__main__":
    main()
