import json


def test_json_1():
    json_str_1 = """{\n    "action": "Final Answer",\n    "action_input": "The code to add the tiff file as an image layer to napari is:\\n\\n```python\\nimport napari\\nfrom skimage import io\\nimage = io.imread(\'https://people.math.sc.edu/Burkardt/data/tif/at3_1m4_01.tif\')\\nviewer.add_image(image)\\n```"\n}"""
    json_1 = json.loads(json_str_1)
    print(json_1)


json_str_2 = """{
    "action": "Final Answer",
    "action_input": "To put the data of the second layer in a variable called 'result' and add it as a labels layer, you can use the following code:\n\n```python\nresult = viewer.layers[1].data\nviewer.add_labels(result)\n```"
}"""
def test_json_2():
    json_2 = json.loads(json_str_2)
    print(json_2)

json_str_3 = """{
    "action": "PythonFunctionsTool",
    "action_input": "glob.glob(os.path.join(os.path.expanduser('~'), '**', '*.tiff'), recursive=True)"
}"""

def test_json_3():
    json_3 = json.loads(json_str_3)
    print(json_3)
