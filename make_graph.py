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
import json
import pickle


def schema_to_graph(conn):
    cursor = conn.cursor()

    # Query to get all tables
    cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    tables = cursor.fetchall()

    # Create a graph
    G = nx.Graph()

    # Iterate over each table
    for table_name in tables:
        table_name = table_name[0]

        # Get columns for each table
        cursor.execute(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = '{table_name}';
        """)
        columns = cursor.fetchall()

        column_nodes = []
        for column in columns:
            column_name = f"{table_name}.{column[0]}"  # Node format: TableName.ColumnName
            G.add_node(column_name, metadata={
                'table': table_name,
                'column': column[0],
                'data_type': column[1],
                'is_nullable': column[2] == 'YES',
                'default_value': column[3]
            })
            column_nodes.append(column_name)
        
        # Connect every column to every other column in the same table (complete subgraph)
        for i in range(len(column_nodes)):
            for j in range(i + 1, len(column_nodes)):
                G.add_edge(column_nodes[i], column_nodes[j])

        # Get foreign keys for the table
        cursor.execute(f"""
        SELECT
            kcu.column_name AS source_column,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table_name}';
        """)
        foreign_keys = cursor.fetchall()

        for fk in foreign_keys:
            source_column = f"{table_name}.{fk[0]}"  # Source column
            target_column = f"{fk[1]}.{fk[2]}"  # Target column
            G.add_edge(source_column, target_column, relationship="foreign_key")

    cursor.close()
    return G

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    database="dvdrental", 
    user="postgres", 
    password=os.getenv("DB_PASSWORD"), 
    host="localhost", 
    port="5432"
)

# Get the graph representation of the schema
graph = schema_to_graph(conn)

with open('db_graph.pickle', 'wb') as f:
    pickle.dump(graph, f)

# Convert dictionary metadata to strings (JSON format)
for node, data in graph.nodes(data=True):
    if 'metadata' in data:
        data['metadata'] = json.dumps(data['metadata'])  # Convert dict to JSON string

# Save the graph to a .graphml file
nx.write_graphml(graph, "db.graphml")

# if graph.edges:
#     print("Edges in the graph:")
#     for edge in graph.edges(data=True):
#         print(edge)
# else:
#     print("No edges found in the graph.")

# Close the database connection
conn.close()

# # Draw the graph using matplotlib and networkx
# plt.figure(figsize=(15, 15))  # Increase the figure size for better visibility
# pos = nx.spring_layout(graph, seed=42, k=0.5)  # Position nodes using the spring layout algorithm with adjusted spacing

# # Draw the nodes
# nx.draw_networkx_nodes(graph, pos, node_size=3000, node_color='lightblue')

# # Draw the edges
# nx.draw_networkx_edges(graph, pos, edge_color='gray', width=2)  # Draw edges with a different color and width

# # Draw node labels
# nx.draw_networkx_labels(graph, pos, font_size=10, font_family="sans-serif")

# # Draw edge labels (if needed, like for showing foreign key relationships)
# edge_labels = nx.get_edge_attributes(graph, 'relationship')
# nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

# # Show the plot
# plt.title("Database Schema Graph")
# plt.axis("off")
# plt.show()