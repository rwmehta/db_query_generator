import psycopg2
from openai import OpenAI

import json

from nicegui import ui

OPENAI_API_KEY = ""
# 'not-set'  # TODO: set your OpenAI API key here

client = OpenAI(api_key=OPENAI_API_KEY)

conn = psycopg2.connect(database="dvdrental", user="postgres", password="", host="localhost", port="5432")
with open('database_description.txt', 'r') as file:
    # Read the entire file
    content = file.read()

user_prompt = ""
db_info = content

@ui.page('/')
def main():
   

    async def send() -> None:
        question = text.value
        text.value = ''

        with message_container:
            ui.chat_message(text=question, name='You', sent=True)
            response_message = ui.chat_message(name='Bot', sent=False)
            spinner = ui.spinner(type='dots')

        response = ''

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
                            f"DB: {db_info}"
                            f"Task: {question}"
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

        response_message.clear()

        
        json_object = json.loads(out)

        query = json_object["query"]
        print(query)
        cur = conn.cursor()
        cur.execute(query)
        output = cur.fetchall()

        with response_message:
            ui.html(output)
        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
        # txt.insert(END, "\n" + "Bot -> " + str(output))

        # with message_container:
        #     ui.chat_message(text=question, name='You', sent=True)
        #     response_message = ui.chat_message(name='Bot', sent=False)
        # ui.chat_message(output,
        #         name='Robot',
        #         stamp='now',
        #         avatar='https://robohash.org/ui')

        
        cur.close()
        message_container.remove(spinner)

    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')

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
            placeholder = 'message' if OPENAI_API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')


ui.run(title='Chat with Query Generator')