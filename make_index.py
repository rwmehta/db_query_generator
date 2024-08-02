from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "db-trial-2"

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

    table_entries = []
    current_table = ''
    table_description = ''

    for line in lines:
        line = line.strip()
        if ':' in line and not line.startswith('-'):
            current_table, table_description = line.split(':', 1)
            current_table = current_table.strip()
            table_description = table_description.strip()
        elif line.startswith('-'):
            column_name, column_detail = line.split(':', 1)
            column_detail = column_detail.strip()
            column_name = column_name.strip('- ').strip()
            table_entries.append(f'Table: {current_table} - Description: {table_description} - Column: {column_name} - Detail: {column_detail}')

    return table_entries

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