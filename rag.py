# def parse_table_columns(file_path):
#     with open(file_path, 'r') as file:
#         lines = file.readlines()

#     tables = []
#     current_table = ''
#     current_columns = []

#     for line in lines:
#         line = line.strip()
#         if ':' in line and not line.startswith('-'):
#             if current_table:
#                 table_string = f'Table: {current_table} - Columns: {"; ".join(current_columns)}'
#                 tables.append(table_string)
#             current_table = line.split(':')[0].strip()
#             current_columns = []
#         elif line.startswith('-'):
#             column_name, column_detail = line.split(':', 1)
#             column_detail = column_detail.strip()
#             column_name = column_name.strip('- ').strip()
#             current_columns.append(f'{column_name}: {column_detail}')

#     if current_table:
#         table_string = f'Table: {current_table} - Columns: {"; ".join(current_columns)}'
#         tables.append(table_string)

#     return tables

# # Example usage
# file_path = './database_description.txt'
# text_lines = parse_table_columns(file_path)

# from openai import OpenAI
# import os
# from dotenv import load_dotenv, dotenv_values 
# load_dotenv() 
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def emb_text(text):
#     return (
#         openai_client.embeddings.create(input=text, model="text-embedding-3-small")
#         .data[0]
#         .embedding
#     )

# test_embedding = emb_text("This is a test")
# embedding_dim = len(test_embedding)
# print(embedding_dim)
# print(test_embedding[:10])


# from pymilvus import MilvusClient

# milvus_client = MilvusClient(uri="./milvus_demo.db")

# collection_name = "my_rag_collection"

# if milvus_client.has_collection(collection_name):
#     milvus_client.drop_collection(collection_name)


# milvus_client.create_collection(
#     collection_name=collection_name,
#     dimension=embedding_dim,
#     metric_type="IP",  # Inner product distance
#     consistency_level="Strong",  # Strong consistency level
# )

# from tqdm import tqdm

# data = []

# for i, line in enumerate(tqdm(text_lines, desc="Creating embeddings")):
#     data.append({"id": i, "vector": emb_text(line), "text": line})

# milvus_client.insert(collection_name=collection_name, data=data)


# question = "How is data stored in milvus?"


# search_res = milvus_client.search(
#     collection_name=collection_name,
#     data=[
#         emb_text(question)
#     ],  # Use the `emb_text` function to convert the question to an embedding vector
#     limit=3,  # Return top 3 results
#     search_params={"metric_type": "IP", "params": {}},  # Inner product distance
#     output_fields=["text"],  # Return the text field
# )

# import json

# retrieved_lines_with_distances = [
#     (res["entity"]["text"], res["distance"]) for res in search_res[0]
# ]
# print(json.dumps(retrieved_lines_with_distances, indent=4))

from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "db-trial-2"
index = pc.Index(index_name)

import openai 
openai.api_key = os.getenv("OPENAI_API_KEY")

# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed(docs: list[str]) -> list[list[float]]:
    res = openai.embeddings.create(
        input=docs,
        model="text-embedding-ada-002"
    )
    doc_embeds = [r.embedding for r in res.data] 
    return doc_embeds 

query = "Give me the number of movies rented per year in canada"

x = embed([query])

results = index.query(
    namespace="ns1",
    vector=x[0],
    top_k=50,
    include_values=False,
    include_metadata=True
)

print(results)




