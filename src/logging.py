# setup Arize Phoenix for logging/observability
import phoenix as px
import llama_index.core


def start_log():
    px.launch_app()
    llama_index.core.set_global_handler("arize_phoenix")