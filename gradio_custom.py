# import gradio as gr

# from main import create_and_prepare_query_pipeline

# if __name__ == "__main__":
#     # Create and prepare query pipeline
#     qp= create_and_prepare_query_pipeline(table_infos)
    
#     # pick query from constants
#     query = random.choice(QUERIES) # What is the legal address of <entity name>?
#     print(f"Query1 : {query}")
#     response = qp.run(
#         query=query
#     )
#     print(f"response: {str(response)}")
#     # Run query and print its response
#     # print(run_query(query, query))
#     print("Query ran sucessfully........")

#     # Launch UI
#     # launch_ui()
#     ui = gr.ChatInterface(fn=run_query, examples=QUERIES, title=UI_TITLE)
#     ui.launch(debug=True, share=True)