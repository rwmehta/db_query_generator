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
from collections import Counter
from pinecone_text.hybrid import hybrid_convex_scale

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "db-trial-3"
index = pc.Index(index_name)

import openai 
openai.api_key = os.getenv("OPENAI_API_KEY")

# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from transformers import BertTokenizerFast
# load bert tokenizer from huggingface
tokenizer = BertTokenizerFast.from_pretrained(
    'bert-base-uncased'
)

def embed(docs: list[str]) -> list[list[float]]:
    res = openai.embeddings.create(
        input=docs,
        model="text-embedding-3-large"
    )
    doc_embeds = [r.embedding for r in res.data] 
    return doc_embeds 

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

# query = "Give me the number of movies rented per year in canada"

# dense = embed([query])


def hybrid_scale(dense, sparse, alpha: float):
    # check alpha value is in range
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between 0 and 1")
    # scale sparse and dense vectors to create hybrid search vecs
    hsparse = [{
        'indices': sparse['indices'],
        'values':  [v * (1 - alpha) for v in sparse['values']]
    }]
    hdense = [v * alpha for v in dense[0]]
    return hdense, hsparse


def hybrid_query(question, top_k, alpha):
   # convert the question into a sparse vector
   sparse_vec = generate_sparse_vectors([question])[0]
   # convert the question into a dense vector
   dense_vec = embed([question])
#    print(dense_vec, type(dense_vec))
#    model.encode([question]).tolist()
   # scale alpha with hybrid_scale
   dense_vec, sparse_vec = hybrid_scale(
      dense_vec, sparse_vec, alpha
   )
   # query pinecone with the query parameters
   result = index.query(
      vector=dense_vec,
      sparse_vector=sparse_vec[0],
      top_k=top_k,
      include_metadata=True
   )
   # return search results as json
   return result


# def hybrid_query(question, top_k, alpha):
#     # convert the question into a sparse vector
#     sparse_vec = generate_sparse_vectors([question])
#     s_embed = sparse_vec

#     print(s_embed[0]["indices"], type(s_embed[0]["indices"][0]), s_embed[0]["values"], type(s_embed[0]["values"][0]))

#     # convert the question into a dense vector
#     dense_vec = dense
#     dense_vec, sparse_vector = hybrid_convex_scale(
#         dense_vec, sparse_vec, alpha=alpha
#     )
#     # query pinecone with the query parameters
#     result = index.query(
#         vector=dense_vec,
#         sparse_vector=sparse_vec[0],
#         top_k=top_k,
#         include_metadata=True,
#       )
#     # return search results as json
#     return result

# results = index.query(
#     namespace="ns1",
#     vector=x[0],
#     top_k=50,
#     include_values=False,
#     include_metadata=True
# )

# print(hybrid_query(query, 50, 0.5))




