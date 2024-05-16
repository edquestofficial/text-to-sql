from config.dev.query import QUERIES
from config.dev.constants import  UI_TITLE
import gradio as gr
import main

def launch_ui():
    ui = gr.ChatInterface(fn=main.run_query, examples=QUERIES, title=UI_TITLE)
    ui.launch(debug=True, share=True)