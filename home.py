from nicegui import ui
import psycopg2
from openai import OpenAI
import json
import pandas.io.sql as psql
from matplotlib import pyplot as plt
from functools import partial
import numpy as np
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

@ui.page('/error_page')
def error_page():
    global error
    ui.label(error)
    ui.button('Back', on_click=lambda: ui.navigate.to('/'))

@ui.page('/data_page')
def data_page():
    ui.label('Retrieved Data')

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    conn = psycopg2.connect(database="dvdrental", user="postgres", password=os.getenv("DB_PASSWORD"), host="localhost", port="5432")

    with open('database_description.txt', 'r') as file:
        # Read the entire file
        content = file.read()

    global user_prompt
    db_info = content
    global prev
    global prev_text
    global full_history
    global last_query
    if prev:
        full_history += prev_text
        prev_text = user_prompt


        response1 = client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "You are an assistant that creates PostgreSQL queries based on the database information provided."
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": (
                            f"You will receive four inputs. The first one is a description of the database (starting with 'DB: '), "
                            f"the second is a description of the query you were asked to build until now (starting with 'Task_History: '),"
                            f"the third is the query you have already built based on the task history (starting with 'Prev_Query: '),"
                            f"the fourth is the additional requirements for the query that you must build now. (starting with 'New_Task: ')"
                            f"You should return a JSON in this format:\\n"
                            f'{{"query": "<the text of the query>"}}'
                            f"If the task requested does not fit the tables and columns in the database description"
                            f"You should return a json of this format:\\n"
                            f'{{"error": "<1 sentence describing why this task is not possible>"}}'
                            f"DB: {db_info}"
                            f"Task_History: {full_history}"
                            f"Prev_Query: {last_query}"
                            f"New_Task: {prev_text}"
                        )
                    }
                ]
                },
            ],
            temperature=1,
            max_tokens=1602,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    else:
        full_history = ""
        prev_text = user_prompt

        response1 = client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "You are an assistant that creates PostgreSQL queries based on the database information provided."
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": (
                            f"You will receive two inputs. The first one is a description of the database (starting with 'DB: '), "
                            f"the second is a description of the query you are tasked with creating (starting with 'Task: ')."
                            f"You should return a JSON in this format:\\n"
                            f'{{"query": "<the text of the query>"}}'
                            f"If the task requested does not fit the tables and columns in the database description"
                            f"You should return a json of this format:\\n"
                            f'{{"error": "<1 sentence describing why this task is not possible>"}}'
                            f"DB: {db_info}"
                            f"Task: {user_prompt}"
                        )
                    }
                ]
                },
            ],
            temperature=1,
            max_tokens=1602,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

    # async for chunk in llm.astream(question, config={'callbacks': [NiceGuiLogElementCallbackHandler(log)]}):
    #     response += chunk.content
    out = response1.choices[0].message.content
    print(out)
    json_object = json.loads(out)

    if "error" in json_object:
        # print("here")
        global error
        error = json_object["error"]
        ui.open('/error_page')
    else:
        query = json_object["query"]
        last_query = query
        # print(query)
        # cur = conn.cursor()
        # cur.execute(query)
        # output = cur.fetchall()
        # print(output)
        # ui.html(output)

        # cur.close()
        try:
            df = psql.read_sql(query, conn)
            ui.aggrid.from_pandas(df).classes('max-h-40')
            ui.textarea(label='Text', placeholder='Graph Description',
                on_change=set_equal)
            global graph_var
            print("graph_var", graph_var)
            ui.button('Generate', on_click=partial(make_graph, client, lambda: graph_var, df))
            # cols = list(df.columns)
            # with ui.pyplot(figsize=(6, 4)):
            #     # x=cols[0], y=cols[1],
            #     df.plot.bar( ax=plt.gca())
            conn.close()
            ui.button('Back', on_click=lambda: ui.navigate.to('/'))
        except Exception as excep:

            response2 = client.chat.completions.create(
                model="gpt-4o",
                response_format={ "type": "json_object" },
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": "You are an assistant that creates PostgreSQL queries based on the database information provided."
                        }
                    ]
                    },
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": (
                                f"You will receive four inputs. The first one is a description of the database (starting with 'DB: '), "
                                f"the second is a description of the query you are tasked with creating (starting with 'Task: ')."
                                f"You already had one attempt at creating the query which resulted in the query and exception it caused."
                                f"Your first attempt at a query is the third input (Starting with 'Query: ') and the exception"
                                f"is provided as your fourth input (Starting with 'Exception: '). Using this information adjust the"
                                f" query such that it fulfills the task."
                                f"You should return a JSON in this format:\\n"
                                f'{{"query": "<the text of the query>"}}'
                                f"If the task requested does not fit the tables and columns in the database description"
                                f"You should return a json of this format:\\n"
                                f'{{"error": "<1 sentence describing why this task is not possible>"}}'
                                f"DB: {db_info}"
                                f"Task: {user_prompt}"
                                f"Query: {query}"
                                f"Exception: {excep}"
                            )
                        }
                    ]
                    },
                ],
                temperature=1,
                max_tokens=1602,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # async for chunk in llm.astream(question, config={'callbacks': [NiceGuiLogElementCallbackHandler(log)]}):
            #     response += chunk.content
            out = response2.choices[0].message.content
            print(out)
            json_object = json.loads(out)

            if "error" in json_object:
                # print("here")
                # global error
                error = json_object["error"]
                ui.open('/error_page')
            else:
                query = json_object["query"]
                # print(query)
                # cur = conn.cursor()
                # cur.execute(query)
                # output = cur.fetchall()
                # print(output)
                # ui.html(output)

                # cur.close()
                try:
                    df = psql.read_sql(query, conn)
                    ui.aggrid.from_pandas(df).classes('max-h-40')
                    # cols = list(df.columns)
                    ui.textarea(label='Text', placeholder='Graph Description',
                        on_change=set_equal)
                    # global graph_var

                    ui.button('Generate', on_click=partial(make_graph, client, lambda: graph_var, df))

                    # with ui.pyplot(figsize=(6, 4)):
                    #     # x=cols[0], y=cols[1],
                    #     df.plot.bar( ax=plt.gca())


                    conn.close()
                    ui.button('Back', on_click=lambda: ui.navigate.to('/'))
                except Exception as e:
                    # global error
                    error = e
                    ui.open('/error_page')


        
user_prompt = ""
error = ""
graph_var = ""
prev = False
prev_text = ""
full_history = ""

last_query = ""
def update_user_prompt(e):
    global prev
    prev = False
    global user_prompt
    user_prompt = e.value

def update_history(e):
    global user_prompt
    global prev
    prev = True
    user_prompt = e.value

def set_equal(val):
    global graph_var
    graph_var = val

def make_graph(client, get_graph_var, df):
    graph_var = get_graph_var()
    print("gv 2", graph_var)
    cols = str(list(df.columns))
    response3 = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "You are an assistant that creates python code for Matplotlib graphs based on Pandas dataframes."
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": (
                        f"You will receive two inputs. The first one is a list of columns in the pandas dataframe (starting with 'DF: '), "
                        f"the second is a description of the graph you are tasked with creating (starting with 'Graph: ')."
                        f"If no description is provided create a graph that seems the most reasonable. "
                        f"The code has to be in python and in this format in order to integrate with the gui package being used: "
                        f"with ui.pyplot(figsize=(6, 4)):"
                        f"    df.plot.bar( ax=plt.gca())"
                        f"the dataframe object variable is df, so use that for the graph data."
                        f"if any additional calculations need to be done numpy can be used, which has already been imported as np."
                        f"The value that code corresponds to in the dictionary must be syntactically correct python code that can be run with exec. Absolutely no explanation or extraneous information in the code"
                        f"You should return a JSON in this format:\\n"
                        f'{{"code": "<python code in the given format for the graph>"}}'
                        f"DF: {cols}"
                        f"Graph: {graph_var}"
                    )
                }
            ]
            },
        ],
        temperature=1,
        max_tokens=1602,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    out = response3.choices[0].message.content
    print(out)
    json_object = json.loads(out)
    if "code" in json_object:
        exec(json_object["code"])

@ui.page('/')
def main_page():
    ui.input(label='Question', placeholder='SQL Prompt', on_change=update_user_prompt)
    ui.button('Submit', on_click=lambda: ui.navigate.to('/data_page'))
    ui.label("Previous")
    global prev_text
    ui.label(prev_text)
    ui.input(label='Question', placeholder='SQL Prompt', on_change=update_history)
    ui.button('Add On', on_click=lambda: ui.navigate.to('/data_page'))



ui.run()