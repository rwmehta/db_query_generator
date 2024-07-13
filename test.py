import psycopg2
from openai import OpenAI
client = OpenAI(api_key="")
import json

conn = psycopg2.connect(database="dvdrental", user="postgres", password="", host="localhost", port="5432")

# with open('database_description.txt', 'r') as file:
#     # Read the entire file
#     content = file.read()

# user_prompt = "how many movies were rented per month per country"
# db_info = content

def llm_response():
# response1 = client.chat.completions.create(
#   model="gpt-4o",
#   response_format={ "type": "json_object" },
#   messages=[
#     {
#       "role": "system",
#       "content": [
#         {
#           "type": "text",
#           "text": "You are an assistant that creates PostgreSQL queries based on the database information provided."
#         }
#       ]
#     },
#     {
#       "role": "user",
#       "content": [
#         {
#           "type": "text",
#           "text": (
#                 f"You will receive two inputs. The first one is a description of the database (starting with 'DB: '), "
#                 f"the second is a description of the query you are tasked with creating (starting with 'Task: ')."
#                 f"You should return a JSON in this format:\\n"
#                 f'{{"query": "<the text of the query>"}}'
#                 f"DB: {db_info}"
#                 f"Task: {user_prompt}"
#             )
#         }
#       ]
#     },
#   ],
#   temperature=1,
#   max_tokens=1602,
#   top_p=1,
#   frequency_penalty=0,
#   presence_penalty=0
# )

# out = response1.choices[0].message.content
# print(out)
# json_object = json.loads(out)

# query = json_object["query"]
cur = conn.cursor()
# cur.execute(query)


try:
    cur.execute("SELECT * FROM non_existent_table;")
    output = cur.fetchall()
except Exception as e:
    print("exception is", e)
# # Get all column names for each table
# for table in tables:
#     cur.execute("""SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s""", (table[0],))
#     columns = cur.fetchall()

#     # Print the table and column names
#     print("Table:", table[0])
#     for column in columns:
#         print("Column:", column[0])
# print(output)
cur.close()
conn.close()