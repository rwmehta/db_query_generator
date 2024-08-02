from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "db-trial-1"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536, 
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws", 
            region="us-east-1"
        ) 
    ) 

index = pc.Index(index_name)

def parse_table_columns(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    tables = []
    current_table = ''
    current_columns = []

    for line in lines:
        line = line.strip()
        if ':' in line and not line.startswith('-'):
            if current_table:
                table_string = f'Table: {current_table} - Columns: {"; ".join(current_columns)}'
                tables.append(table_string)
            current_table = line.split(':')[0].strip()
            current_columns = []
        elif line.startswith('-'):
            column_name, column_detail = line.split(':', 1)
            column_detail = column_detail.strip()
            column_name = column_name.strip('- ').strip()
            current_columns.append(f'{column_name}: {column_detail}')

    if current_table:
        table_string = f'Table: {current_table} - Columns: {"; ".join(current_columns)}'
        tables.append(table_string)

    return tables

# Example usage
file_path = './database_description.txt'
text_lines = parse_table_columns(file_path)

data = []
for i in range(len(text_lines)):
    data.append({"id": "vec"+ str(i), "text": text_lines[i]})

print(data)

# from openai import OpenAI
import openai 
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")

# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed(docs: list[str]) -> list[list[float]]:
    res = openai.embeddings.create(
        input=docs,
        model="text-embedding-ada-002"
    )
    doc_embeds = [r.embedding for r in res.data] 
    return doc_embeds 


doc_embeds = embed([d["text"] for d in data])

vectors = []
for d, e in zip(data, doc_embeds):
    vectors.append({
        "id": d['id'],
        "values": e,
        "metadata": {'text': d['text']}
    })

index.upsert(
    vectors=vectors,
    namespace="ns1"
)