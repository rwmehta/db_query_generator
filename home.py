from nicegui import ui
import psycopg2
from openai import OpenAI
import json
import pandas.io.sql as psql
from matplotlib import pyplot as plt

# @ui.page('/other_page')
# def other_page():
#     ui.label('Welcome to the other side')

@ui.page('/data_page')
def dark_page():
    ui.label('Retrieved Data')

    OPENAI_API_KEY = ""

    client = OpenAI(api_key=OPENAI_API_KEY)

    conn = psycopg2.connect(database="dvdrental", user="postgres", password="", host="localhost", port="5432")

    with open('database_description.txt', 'r') as file:
        # Read the entire file
        content = file.read()

    global user_prompt
    db_info = content

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

    query = json_object["query"]
    print(query)
    # cur = conn.cursor()
    # cur.execute(query)
    # output = cur.fetchall()
    # print(output)
    # ui.html(output)

    # cur.close()
    df = psql.read_sql(query, conn)
    ui.aggrid.from_pandas(df).classes('max-h-40')
    cols = list(df.columns)
    with ui.pyplot(figsize=(6, 4)):
        # x=cols[0], y=cols[1],
        df.plot.bar( ax=plt.gca())
    conn.close()
    ui.button('Back', on_click=lambda: ui.navigate.to('/'))
user_prompt = ""

def update_user_prompt(e):
    global user_prompt
    user_prompt = e.value

@ui.page('/')
def main_page():
    ui.input(label='Question', placeholder='SQL Prompt', on_change=update_user_prompt)
    ui.button('Next Page', on_click=lambda: ui.navigate.to('/data_page'))

ui.run()