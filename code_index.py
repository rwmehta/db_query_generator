from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "code-trial-1"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=3072, 
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws", 
            region="us-east-1"
        ) 
    ) 

index = pc.Index(index_name)

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
text_lines = [
    "Create a bar chart comparing quantities of different categories with labels. A bar chart is used to compare quantities of different categories, with bars representing the values.",
    "Create a line chart to show trends over time with labels for the x-axis and y-axis. A line chart is ideal for showing trends over time, depicting changes with lines connecting data points.",
    "Create a pie chart to display the composition of a whole with percentage labels on each slice. A pie chart displays the composition of a whole, where each slice represents a category's contribution to the total.",
    "Create a histogram to show the distribution of a dataset with labeled bins and frequency counts. A histogram shows the distribution of a dataset, useful for understanding the frequency distribution of continuous data.",
    "Create a scatter plot to illustrate the relationship between two variables with labeled axes. A scatter plot illustrates the relationship between two variables, helping identify correlations and patterns.",
    "Create a box plot to summarize data through their quartiles with labeled axes. A box plot summarizes data through their quartiles, useful for spotting outliers and understanding data distribution.",
    "Create a heatmap to display data values as color-coded matrices with a color scale legend. A heatmap displays data values as color-coded matrices, effectively showing the intensity of data at specific points.",
    "Create an area chart to show cumulative data over time with labeled axes. An area chart, similar to a line chart, fills the area below the line to show cumulative data over time.",
    "Create a bubble chart to visualize three dimensions of data with varying bubble sizes and labeled axes. A bubble chart is a variation of a scatter plot, where the size of the bubbles represents an additional variable, useful for visualizing three dimensions of data.",
    "Create a radar chart to display multivariate data with each variable having its own labeled axis. A radar chart displays multivariate data in a two-dimensional chart, with each variable having its own axis starting from the same point.",
    "Create a waterfall chart to show the cumulative effect of sequentially introduced positive or negative values with labeled bars. A waterfall chart shows the cumulative effect of sequentially introduced positive or negative values, useful for understanding how an initial value is affected by a series of intermediate positive or negative values.",
    "Create a Gantt chart to display project schedules and timelines with labeled tasks and time intervals. A Gantt chart is used for project management, displaying project schedules and timelines.",
    "Create a violin plot to understand the distribution and density of data with labeled categories. A violin plot combines aspects of the box plot and density plot, useful for understanding the distribution and density of data.",
    "Create a treemap to display hierarchical data as nested rectangles with proportional sizes and labeled rectangles. A treemap displays hierarchical data as nested rectangles, with each rectangle proportionally sized to reflect a data value."
]

code_blocks = [
    "fig = px.bar(df, x='Categories', y='Values', title='Bar Chart Example')\nfig.update_layout(xaxis_title='Categories', yaxis_title='Values')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.line(df, x='X-axis Label', y='Y-axis Label', title='Line Chart Example')\nfig.update_layout(xaxis_title='X-axis Label', yaxis_title='Y-axis Label')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.pie(df, values='Values', names='Categories', title='Pie Chart Example', hole=0.3)\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.histogram(df, x='Value Bins', nbins=10, title='Histogram Example')\nfig.update_layout(xaxis_title='Value Bins', yaxis_title='Frequency')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.scatter(df, x='x_column', y='y_column', title='Scatter Plot Example')\nfig.update_layout(xaxis_title='X-axis Label', yaxis_title='Y-axis Label')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.box(df, x='Categories', y='Values', title='Box Plot Example')\nfig.update_layout(xaxis_title='Categories', yaxis_title='Values')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.imshow(df.values, labels=dict(x='X-axis Label', y='Y-axis Label', color='Color Scale'), title='Heatmap Example')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.area(df, x='X-axis Label', y='Y-axis Label', title='Area Chart Example')\nfig.update_layout(xaxis_title='X-axis Label', yaxis_title='Y-axis Label')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.scatter(df, x='x_column', y='y_column', size='bubble_size', title='Bubble Chart Example', opacity=0.5)\nfig.update_layout(xaxis_title='X-axis Label', yaxis_title='Y-axis Label')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "categories = list(df.columns[1:])\nfig = go.Figure()\nfig.add_trace(go.Scatterpolar(r=df.loc[0, categories].values, theta=categories, fill='toself'))\nfig.update_layout(polar=dict(radialaxis=dict(visible=True)), title='Radar Chart Example')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = go.Figure(go.Waterfall(name='Values', orientation='v', measure=['relative'] * len(df['Values']), x=df['Categories'], y=df['Values'], connector={'line':{'color':'rgb(63, 63, 63)'}}))\nfig.update_layout(title='Waterfall Chart Example', xaxis_title='Categories', yaxis_title='Values')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.timeline(df, x_start='Start', x_end='End', y='Task', title='Gantt Chart Example')\nfig.update_layout(xaxis_title='Time', yaxis_title='Tasks')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.violin(df, x='Categories', y='Values', title='Violin Plot Example')\nfig.update_layout(xaxis_title='Categories', yaxis_title='Values')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')",
    "fig = px.treemap(df, path=['labels'], values='values', title='Treemap Example')\nui.plotly(fig).classes('w-full h-40').style('width: 600px; height: 300px')"
]



data = []
for i in range(len(text_lines)):
    data.append({"id": "vec"+ str(i), "text": text_lines[i]})

print(data)

# from openai import OpenAI
import openai 
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")

# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed(docs: list[str]) -> list[list[float]]:
    res = openai.embeddings.create(
        input=docs,
        model="text-embedding-3-large"
    )
    doc_embeds = [r.embedding for r in res.data] 
    return doc_embeds 


doc_embeds = embed([d["text"] for d in data])

vectors = []
for d, e, c in zip(data, doc_embeds, code_blocks):
    vectors.append({
        "id": d['id'],
        "values": e,
        "metadata": {'code': c}
    })

index.upsert(
    vectors=vectors,
    namespace="ns1"
)