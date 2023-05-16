class ExampleOmegaTool():
    # These class fields are mandatory:
    name = 'ToolName'
    type = ''
    description = 'Tool description for agent, keep short and clear...'
    prompt = 'Prompt for Tools LLM, if None no LLM is run '
    return_direct = False  # if True immediately returns after calling this tool.

    def run(self, **kwargs) -> str:

        # We get kwargs so we can easily extend this function's signature!

        # Query/Inout received by tool:
        query = kwargs['query']

        # code generated bhy LLM, if prompt is not None:
        code = kwargs['code']

        # Napari viewer instance:
        # Note: this function runs in the 'right' thread so you can safely call the napari viewer.
        viewer = kwargs['viewer']

        # Do something smart here...

        # decide if thinsg worked out:
        success = True

        if success:
            return f"Success: .... !"
        else:
            return f"Failure: .... !"
