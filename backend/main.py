import hashlib
import json
import os
from pathlib import Path
from openai import OpenAI
import secrets

BASE_DIR = Path(__file__).resolve().parent
QUESTION_TYPES_PATH = BASE_DIR / "query_types.json"

def hashFunction(data) -> str:
    serialized_data = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized_data + secrets.token_bytes(32)).hexdigest()


with QUESTION_TYPES_PATH.open(encoding="utf-8") as question_types_file:
    question_types = json.load(question_types_file)


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=api_key)

def make_prompt(query: str):
    return ("""
    Respond to this prompt with a JSON object ONLY! No other output.
                    
    Consider the following query types with parameters:"""
    + str(question_types)
    + """
    The keys in the parameter list represent the paremeters, and the values of those keys
    represent the data types that those parameters are.
    
    Given the following query:"""
    +  query
    + """, identify which query type it is and what
        the relevant parameters are.

        Print the output as a JSON object of the following form:

        {
            "query_type": ....,
            "parameters": ....
        }

        If the query is empty or doesn't make sense, say that it is an unsupported query_type
    """)

def get_query_details(query: str) -> dict:
    client = get_openai_client()
    response = client.completions.create(
        model = "gpt-3.5-turbo-instruct",
        prompt = make_prompt(query),
        max_tokens=1000
    )
    return json.loads(response.to_dict()['choices'][0]['text'])
