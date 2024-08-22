# from pinecone.grpc import PineconeGRPC as Pinecone
# from pinecone import ServerlessSpec
# import os
# from dotenv import load_dotenv, dotenv_values 
# load_dotenv() 

# pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# index_name = "db-trial-2"

# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         name=index_name,
#         dimension=1536, 
#         metric="cosine", 
#         spec=ServerlessSpec(
#             cloud="aws", 
#             region="us-east-1"
#         ) 
#     ) 

# index = pc.Index(index_name)

# def parse_table_columns(file_path):
#     with open(file_path, 'r') as file:
#         lines = file.readlines()

#     table_entries = []
#     current_table = ''
#     table_description = ''

#     for line in lines:
#         line = line.strip()
#         if ':' in line and not line.startswith('-'):
#             current_table, table_description = line.split(':', 1)
#             current_table = current_table.strip()
#             table_description = table_description.strip()
#         elif line.startswith('-'):
#             column_name, column_detail = line.split(':', 1)
#             column_detail = column_detail.strip()
#             column_name = column_name.strip('- ').strip()
#             table_entries.append(f'Table: {current_table} - Description: {table_description} - Column: {column_name} - Detail: {column_detail}')

#     return table_entries

# # Example usage
# file_path = './database_description.txt'
# text_lines = parse_table_columns(file_path)


# data = []
# for i in range(len(text_lines)):
#     data.append({"id": "vec"+ str(i), "text": text_lines[i]})

# print(data)

# # from openai import OpenAI
# import openai 
# import os
# from dotenv import load_dotenv, dotenv_values 
# load_dotenv() 
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def embed(docs: list[str]) -> list[list[float]]:
#     res = openai.embeddings.create(
#         input=docs,
#         model="text-embedding-ada-002"
#     )
#     doc_embeds = [r.embedding for r in res.data] 
#     return doc_embeds 


# doc_embeds = embed([d["text"] for d in data])

# vectors = []
# for d, e in zip(data, doc_embeds):
#     vectors.append({
#         "id": d['id'],
#         "values": e,
#         "metadata": {'text': d['text']}
#     })

# index.upsert(
#     vectors=vectors,
#     namespace="ns1"
# )

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from collections import Counter
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
from transformers import BertTokenizerFast
import openai 
# load bert tokenizer from huggingface
tokenizer = BertTokenizerFast.from_pretrained(
    'bert-base-uncased'
)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "db-trial-3"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=3072, 
        metric="dotproduct", 
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
contexts = parse_table_columns(file_path)

def build_dict(input_batch):
  # store a batch of sparse embeddings
    sparse_emb = []
    # iterate through input batch
    for token_ids in input_batch:
        indices = []
        values = []
        # convert the input_ids list to a dictionary of key to frequency values
        d = dict(Counter(token_ids))
        # remove special tokens and append sparse vectors to sparse_emb list
        for idx in d:
            if idx not in [101, 102, 103, 0]:
                indices.append(idx)
                values.append(float(d[idx]))
        
        sparse_emb.append({'indices': indices, 'values': values})
        # sparse_emb.append({key: d[key] for key in d if key not in [101, 102, 103, 0]})
    # return sparse_emb list
    return sparse_emb

def generate_sparse_vectors(context_batch):
    # create batch of input_ids
    inputs = tokenizer(
            context_batch, padding=True,
            truncation=True,
            max_length=512
    )['input_ids']
    # create sparse dictionaries
    sparse_embeds = build_dict(inputs)
    return sparse_embeds



openai.api_key = os.getenv("OPENAI_API_KEY")


def embed(docs: list[str]) -> list[list[float]]:
    res = openai.embeddings.create(
        input=docs,
        model="text-embedding-3-large"
    )
    doc_embeds = [r.embedding for r in res.data] 
    return doc_embeds 


doc_embeds = embed(contexts)
s_embed = generate_sparse_vectors(contexts)
print(s_embed[0]["indices"], type(s_embed[0]["indices"][0]), s_embed[0]["values"], type(s_embed[0]["values"][0]))

vectors = []
for i in range(len(contexts)):
    context = contexts[i]
    dense_embeds = doc_embeds[i]
    # create sparse vectors
    sparse_embeds = s_embed[i]

    vectors.append({
        'id': str(i),
        'sparse_values': sparse_embeds,
        'values': dense_embeds,
        'metadata': {'context': context}
    })

    # upload the documents to the new hybrid index
index.upsert(vectors=vectors)

# show index description after uploading the documents
index.describe_index_stats()