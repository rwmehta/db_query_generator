from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from collections import Counter
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
from transformers import BertTokenizerFast
import openai 

import psycopg2
import networkx as nx
import matplotlib.pyplot as plt
import pickle

from networkx.algorithms import approximation

with open('db_graph.pickle', 'rb') as f:
    graph = pickle.load(f)

# Define the start and end nodes for the search
# start_node = 'rental.rental_id'
# end_node = 'country.country_id'
def build_graph(terminal_nodes= ['rental.rental_id', 'country.country_id', 'category.name', 'payment.customer_id']):

    # terminal_nodes = ['rental.rental_id', 'country.country_id', 'category.name', 'payment.customer_id']


    # Find the shortest path
    try:
        # shortest_path = nx.shortest_path(graph, source=start_node, target=end_node)
        # print("Shortest path:", shortest_path)

        # Extract the subgraph containing only the nodes and edges in the shortest path
        steiner_subgraph = approximation.steiner_tree(graph, terminal_nodes, weight='weight', method='mehlhorn')

        # Display nodes and edges in the path
        # Display nodes and edges in the Steiner tree
        print("\nNodes in the Steiner tree:")
        for node in steiner_subgraph.nodes(data=False):
            print(node)

        return(list(steiner_subgraph))

        # print("\nEdges in the Steiner tree:")
        # for edge in steiner_subgraph.edges(data=True):
        #     print(edge)
        
        # Visualize the Steiner tree
        # plt.figure(figsize=(8, 8))
        # pos = nx.spring_layout(steiner_subgraph, seed=42)  # Use a fixed seed for consistent layout

        # # Draw nodes
        # nx.draw_networkx_nodes(steiner_subgraph, pos, node_size=3000, node_color='lightgreen')

        # # Draw edges
        # nx.draw_networkx_edges(steiner_subgraph, pos, edge_color='blue', width=2)

        # # Draw labels
        # nx.draw_networkx_labels(steiner_subgraph, pos, font_size=10, font_family='sans-serif')

        # plt.title("Steiner Tree")
        # plt.axis("off")
        # plt.show()

    except nx.NetworkXNoPath:
        print(f"No path found connecting all terminal nodes: {terminal_nodes}")

##########################################################################################################
import re

# Function to extract table_name.column_name
def extract_table_column_name(metadata):
    context = metadata['context']
    
    # Use regex to extract table and column names
    table_name = re.search(r'Table: (\w+)', context).group(1)
    column_name = re.search(r'Column: (\w+)', context).group(1)
    
    return f"{table_name}.{column_name}"

# Loop through the matches and extract the table_name.column_name
def vec_to_col(vecs):
    terminal_nodes = []
    print("Vector to Column")
    for match in vecs['matches']:
        table_column = extract_table_column_name(match['metadata'])
        terminal_nodes.append(table_column)
        print(table_column)

    return terminal_nodes





import json

def load_json_as_dict(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def get_values_for_keys(data, keys):
    return [data[key] for key in keys if key in data]

def build_context(keys_to_retrieve):
    # Example usage
    json_file_path = './table_columns.json'
     

    # Load the JSON as a dictionary
    data = load_json_as_dict(json_file_path)

    # Get the values for the specified keys
    retrieved_values = get_values_for_keys(data, keys_to_retrieve)

    # Print the retrieved values
    # print(json.dumps(retrieved_values, indent=4))
    return retrieved_values




# print(build_graph())

import rag

def all_together(query = "Give me the number of movies rented per year in canada", k = 25, alpha = 0.5):
    
    vecs = rag.hybrid_query(query, k, alpha)

    t_nodes = vec_to_col(vecs)

    s_graph = build_graph(t_nodes)

    final_context = build_context(s_graph)
    return final_context
    # print(final_context, len(final_context))


# all_together()