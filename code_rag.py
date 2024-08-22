from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "code-trial-1"
index = pc.Index(index_name)

import openai 
openai.api_key = os.getenv("OPENAI_API_KEY")

# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed(docs: list[str]) -> list[list[float]]:
    res = openai.embeddings.create(
        input=docs,
        model="text-embedding-3-large"
    )
    doc_embeds = [r.embedding for r in res.data] 
    return doc_embeds 

def code_search(query):

    # query = "make a bar graph"

    x = embed([query])

    results = index.query(
        namespace="ns1",
        vector=x[0],
        top_k=1,
        include_values=False,
        include_metadata=True
    )
    return results

# print(results)

# from nicegui import ui
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go

# data = {
#     'Categories': ['A', 'B', 'C', 'D', 'E'],
#     'Values': [23, 17, 35, 29, 12]
# }
# df = pd.DataFrame(data)


# @ui.page('/')
# def main():
#     ui.markdown('# Radar Chart Example')
#     with ui.card():
#         exec(results['matches'][0]['metadata']['code'])

# ui.run()



# sum_check = (
#                             f"You will receive four inputs. The first one is a list of columns in the pandas dataframe (starting with 'DF: '), "
#                             f"the second is a description of the graph or change in the graph you are tasked with creating (starting with 'Graph: '), "
#                             f"the third is the history of the graphing requests up to this point, this may be empty for the first request (starting with 'History: '), "
#                             f"finally there is the psql query that generated this graph (starting with 'Query: ')"
#                             f"The code has to be in python and in this format in order to integrate with the gui package being used: \\n"
#                             f"fig = px.bar(df, x='Categories', y='Values', title='Bar Chart Example')"
#                             f"fig.update_layout(xaxis_title='Categories', yaxis_title='Values')"
#                             f"ui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')"
#                             f"\\n the pandas dataframe object variable is df, so use that for the graph data."
#                             f"if any additional calculations need to be done numpy can be used, which has already been imported as np."
#                             f"Only plotly should be used for graphing and plotly.express as px and plotly.graph_objects as go have already been imported."
#                             f"There should never be any additional imports regardless of the description of the graph you have been tasked with."
#                             f"The value that code corresponds to in the dictionary must be syntactically correct python code that can be run with exec. Absolutely no explanation or extraneous information in the code"
#                             f"Make absolutely sure there is proper spacing so the code can be run with exec()."
#                             f"You should return a JSON in this format:\\n"
#                             f'{{"code": "<python code in the given format for the graph>"}}'
#                             f"If no description is provided or the task is not applicable to graphing return JSON in this format:\\n"
#                             f'{{"error": "<1 sentence explanation for why the graph cannot be created.>"}}'                            
#                             f"DF: {cols}"
#                             f"Graph: {graph_var}"
#                             f"History: {graph_history}"
#                             f"Query: {query}"
#                         )