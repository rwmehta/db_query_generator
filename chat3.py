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
import tiktoken
load_dotenv() 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


with open('database_description.txt', 'r') as file:
    # Read the entire file
    content = file.read()

# user_prompt = ""
db_info = content

@ui.page('/')
def main():
    def remove_import_lines(code: str) -> str:
        lines = code.split('\n')
        filtered_lines = [line for line in lines if not line.strip().startswith('import')]
        return '\n'.join(filtered_lines)

    def token_counter(string: str, encoding_name: str) -> str:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        if num_tokens > 16000:
            return "summarize"
        else:
            return "continue"

    def summary(history: str) -> str:
        response1 = client.chat.completions.create(
                model="gpt-4o",
                response_format={ "type": "json_object" },
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": "You are an assistant that summarizes a set of requests."
                        }
                    ]
                    },
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": (
                                f"You will receive one input. It is a history of the requests (starting with 'History: '), "
                                f"Summarize this history, the instructions that appear lower down in the history are more important as they are the most recent, "
                                f"so prioritze those. The summary must be 200 words or less."
                                f"You should return a JSON in this format:\\n"
                                f'{{"Summary": "<the summarized history of requests>"}}'
                                f"History: {history}"
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
        
        out = response1.choices[0].message.content
        # print(out)
        json_object = json.loads(out)
        try:
            return json_object["Summary"]
        except:
            summary(history)

    async def make_graph() -> None:
        graph_var = text.value
        text.value = ''
        nonlocal graph_history
        with message_container:
            ui.chat_message(text=graph_var, name='You', sent=True)
            response_message = ui.chat_message(name='Bot', sent=False)
            spinner = ui.spinner(type='dots')
        
        cols = str(list(df.columns))

        response_message.clear()
        sum_check = (
                            f"You will receive four inputs. The first one is a list of columns in the pandas dataframe (starting with 'DF: '), "
                            f"the second is a description of the graph or change in the graph you are tasked with creating (starting with 'Graph: '), "
                            f"the third is the history of the graphing requests up to this point, this may be empty for the first request (starting with 'History: '), "
                            f"finally there is the psql query that generated this graph (starting with 'Query: ')"
                            f"The code has to be in python and in this format in order to integrate with the gui package being used: "
                            f"with ui.pyplot(figsize=(6, 4)):"
                            f"    df.plot.bar( ax=plt.gca())"
                            f"the dataframe object variable is df, so use that for the graph data."
                            f"if any additional calculations need to be done numpy can be used, which has already been imported as np."
                            f"There should never be any additional imports regardless of the description of the graph you have been tasked with."
                            f"The value that code corresponds to in the dictionary must be syntactically correct python code that can be run with exec. Absolutely no explanation or extraneous information in the code"
                            f"You should return a JSON in this format:\\n"
                            f'{{"code": "<python code in the given format for the graph>"}}'
                            f"If no description is provided or the task is not applicable to graphing return JSON in this format:\\n"
                            f'{{"error": "<1 sentence explanation for why the graph cannot be created.>"}}'                            
                            f"DF: {cols}"
                            f"Graph: {graph_var}"
                            f"History: {graph_history}"
                            f"Query: {query}"
                        )
        
        tk_count = token_counter(sum_check, "o200k_base")
        if tk_count == "summarize":
            graph_history = summary(graph_history)
            sum_check = (
                            f"You will receive four inputs. The first one is a list of columns in the pandas dataframe (starting with 'DF: '), "
                            f"the second is a description of the graph or change in the graph you are tasked with creating (starting with 'Graph: '), "
                            f"the third is the history of the graphing requests up to this point, this may be empty for the first request (starting with 'History: '), "
                            f"finally there is the psql query that generated this graph (starting with 'Query: ')"
                            f"The code has to be in python and in this format in order to integrate with the gui package being used: "
                            f"with ui.pyplot(figsize=(6, 4)):"
                            f"    df.plot.bar( ax=plt.gca())"
                            f"the dataframe object variable is df, so use that for the graph data."
                            f"if any additional calculations need to be done numpy can be used, which has already been imported as np."
                            f"There should never be any additional imports regardless of the description of the graph you have been tasked with."
                            f"The value that code corresponds to in the dictionary must be syntactically correct python code that can be run with exec. Absolutely no explanation or extraneous information in the code"
                            f"You should return a JSON in this format:\\n"
                            f'{{"code": "<python code in the given format for the graph>"}}'
                            f"If no description is provided or the task is not applicable to graphing return JSON in this format:\\n"
                            f'{{"error": "<1 sentence explanation for why the graph cannot be created.>"}}'                            
                            f"DF: {cols}"
                            f"Graph: {graph_var}"
                            f"History: {graph_history}"
                            f"Query: {query}"
                        )
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
                    "text": sum_check
                    
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

        graph_history += " " + graph_var

        out = response3.choices[0].message.content
        print(out)
        json_object = json.loads(out)
        if "error" in json_object:
            error = json_object["error"]
            with response_message:
                ui.html(error)
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
            message_container.remove(spinner)
            return
        else:
            try:
                if "code" in json_object:
                    code = json_object["code"]
                    code = remove_import_lines(code)
                    with ui.dialog() as dialog, ui.card():
                            ui.label(query)
                    with response_message:
                        exec(json_object["code"])
                        ui.button(icon="code").on('click', dialog.open)
                    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                    message_container.remove(spinner)
                    return
            except Exception as e:
                        with response_message:
                            ui.html(str(e))
                        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                        message_container.remove(spinner)
                        return
                    
        


    async def make_query() -> None:

        conn = psycopg2.connect(database="dvdrental", user="postgres", password=os.getenv("DB_PASSWORD"), host="localhost", port="5432")

        nonlocal history
        nonlocal query
        nonlocal df
        print(history)
        user_prompt = text.value
        text.value = ''

        with message_container:
            ui.chat_message(text=user_prompt, name='You', sent=True)
            response_message = ui.chat_message(name='Bot', sent=False)
            spinner = ui.spinner(type='dots')

        response_message.clear()

        if history == "":
            history += " " + user_prompt
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
                                f"Complete the following two steps: \\n"
                                f"1. Determine which tables have each piece of information desired, and what other tables or fields create connections between them."
                                f"2. Use all the functionalities of postgres sql to create the query for the task and the set of tables, you may join as many tables as neccessary."
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
        else:
            sum_check = (
                                f"You will receive four inputs. The first one is a description of the database (starting with 'DB: '), "
                                f"the second is a description of the query you were asked to build until now (starting with 'Task_History: '),"
                                f"the third is the query you have already built based on the task history (starting with 'Prev_Query: '),"
                                f"the fourth is the additional requirements for the query that you must build now. (starting with 'New_Task: ')"
                                f"Complete the following two steps: \\n"
                                f"1. Determine which tables have each piece of information desired, and what other tables or fields create connections between them."
                                f"2. Use all the functionalities of postgres sql to create the query for the task and the set of tables, you may join as many tables as neccessary."
                                f"You should return a JSON in this format:\\n"
                                f'{{"query": "<the text of the query>"}}'
                                f"If the task requested does not fit the tables and columns in the database description"
                                f"You should return a json of this format:\\n"
                                f'{{"error": "<1 sentence describing why this task is not possible>"}}'
                                f"DB: {db_info}"
                                f"Task_History: {history}"
                                f"Prev_Query: {query}"
                                f"New_Task: {user_prompt}"
                            )
            tk_count = token_counter(sum_check, "o200k_base")
            if tk_count == "summarize":
                history = summary(history)
                sum_check = (
                                f"You will receive four inputs. The first one is a description of the database (starting with 'DB: '), "
                                f"the second is a description of the query you were asked to build until now (starting with 'Task_History: '),"
                                f"the third is the query you have already built based on the task history (starting with 'Prev_Query: '),"
                                f"the fourth is the additional requirements for the query that you must build now. (starting with 'New_Task: ')"
                                f"Complete the following two steps: \\n"
                                f"1. Determine which tables have each piece of information desired, and what other tables or fields create connections between them."
                                f"2. Use all the functionalities of postgres sql to create the query for the task and the set of tables, you may join as many tables as neccessary."
                                f"You should return a JSON in this format:\\n"
                                f'{{"query": "<the text of the query>"}}'
                                f"If the task requested does not fit the tables and columns in the database description"
                                f"You should return a json of this format:\\n"
                                f'{{"error": "<1 sentence describing why this task is not possible>"}}'
                                f"DB: {db_info}"
                                f"Task_History: {history}"
                                f"Prev_Query: {query}"
                                f"New_Task: {user_prompt}"
                            )

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
                        "text": sum_check
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
            history += " " + user_prompt

        out = response1.choices[0].message.content
        
        json_object = json.loads(out)
        print("first", json_object)
        if "error" in json_object:
            error = json_object["error"]
            with response_message:
                ui.html(error)
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
            message_container.remove(spinner)
            conn.close()
            return
        else:
            try:
                query = json_object["query"]
                print("2nd", query)
                df = psql.read_sql(query, conn)
                # print(df)

                if not df.empty:
                    with ui.dialog() as dialog, ui.card():
                            ui.label(query)
                    with response_message:
                        ui.aggrid.from_pandas(df).classes('max-h-40').style('width: 400px; height: 300px')
                        ui.button(icon="code").on('click', dialog.open)
                else:
                    with response_message:
                        ui.html("There was no data for this request.")
                ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                message_container.remove(spinner)
                conn.close()
                return
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
                                    f"Complete the following two steps: \\n"
                                    f"1. Determine which tables have each piece of information desired, and what other tables or fields create connections between them."
                                    f"2. Use all the functionalities of postgres sql to create the query for the task and the set of tables, you may join as many tables as neccessary."
                                    f"You should return a JSON in this format:\\n"
                                    f'{{"query": "<the text of the query>"}}'
                                    f"If the task requested does not fit the tables and columns in the database description"
                                    f"You should return a json of this format:\\n"
                                    f'{{"error": "<1 sentence describing why this task is not possible>"}}'
                                    f"DB: {db_info}"
                                    f"Task: {history}"
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

                out = response2.choices[0].message.content
                json_object = json.loads(out)
                print("3rd", excep, json_object)
                if "error" in json_object:
                    error = json_object["error"]
                    with response_message:
                        ui.html(error)
                    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                    message_container.remove(spinner)
                    conn.close()
                    return
                else:
                    query = json_object["query"]

                    try:
                        df = psql.read_sql(query, conn)
                        with ui.dialog() as dialog, ui.card():
                            ui.label(query)
                        with response_message:
                            ui.aggrid.from_pandas(df).classes('max-h-40')
                            ui.button(icon="code").on('click', dialog.open)
                        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                        message_container.remove(spinner)
                        conn.close()
                        return
                    except Exception as e:
                        with response_message:
                            ui.html(str(e))
                        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                        message_container.remove(spinner)
                        conn.close()
                        return
        # query = json_object["query"]
        # print(query)
        # cur = conn.cursor()
        # cur.execute(query)
        # output = cur.fetchall()

        # df = psql.read_sql(query, conn)

        # with response_message:
        #     ui.html(output)
        #     ui.aggrid.from_pandas(df).classes('max-h-40')
        # ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
        # # txt.insert(END, "\n" + "Bot -> " + str(output))

        # # with message_container:
        # #     ui.chat_message(text=question, name='You', sent=True)
        # #     response_message = ui.chat_message(name='Bot', sent=False)
        # # ui.chat_message(output,
        # #         name='Robot',
        # #         stamp='now',
        # #         avatar='https://robohash.org/ui')

        
        # cur.close()
        # message_container.remove(spinner)

    async def clear_history() -> None:
        nonlocal history
        nonlocal graph_history
        nonlocal message_container
        print("in clear")
        message_container.clear()
        history = ""
        graph_history = ""

    history = ""
    query = ""
    df = ""
    graph_history = ""

    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')
    ui.button(icon="restart_alt").on('click', clear_history)
    # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
    ui.query('.q-page').classes('flex')
    ui.query('.nicegui-content').classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('Chat')
        logs_tab = ui.tab('Logs')
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        message_container = ui.tab_panel(chat_tab).classes('items-stretch')
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            # placeholder = 'message' if OPENAI_API_KEY != 'not-set' else \
            #     'Please provide your OPENAI key in the Python script first!'
            text = ui.input(placeholder="placeholder").props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', make_query)
            ui.button(icon="bar_chart").on('click', make_graph)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')


ui.run(title='Chat with Query Generator')