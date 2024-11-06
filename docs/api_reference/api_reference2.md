# API Reference

This section provides detailed documentation of the core classes and utility functions used in GenSphere, specifically focusing on the `visualizer.py`, `graph_builder.py`, and `hub.py` modules.

---

## Core Classes

- [Visualizer](#visualizer)
- [Hub](#hub)

## Utility Functions

- [parse_yaml](#parse_yaml)
- [extract_referenced_nodes](#extract_referenced_nodes)
- [traverse_node_fields](#traverse_node_fields)
- [identify_and_style_entrypoints_outputs](#identify_and_style_entrypoints_outputs)
- [build_graph_data](#build_graph_data)

---

## Visualizer

**Module:** `visualizer.py`

The `Visualizer` class provides a graphical representation of GenSphere workflows using a web-based interface powered by Dash and Cytoscape. It allows users to visualize nodes, their types, dependencies, and inspect details of each node interactively.

### Class Definition

```python
class Visualizer:
    def __init__(self, yaml_file=None, functions_filepath=None, structured_output_schema_filepath=None, address='127.0.0.1', port=8050):
        # Initialization code

    def start_visualization(self):
        # Starts the Dash application for visualization
```

### Constructor

```python
def __init__(self, yaml_file=None, functions_filepath=None, structured_output_schema_filepath=None, address='127.0.0.1', port=8050):
```

**Parameters:**

- `yaml_file` (_str_, optional): Path to the YAML file defining the workflow.
- `functions_filepath` (_str_, optional): Path to the Python file containing custom function definitions.
- `structured_output_schema_filepath` (_str_, optional): Path to the Python file containing structured output schemas.
- `address` (_str_, optional): The IP address to host the Dash app (default: `'127.0.0.1'`).
- `port` (_int_, optional): The port to host the Dash app (default: `8050`).

**Description:**

Initializes the `Visualizer` instance by setting up the necessary file paths and loading the user-provided functions and schemas. It validates the existence and correctness of the provided files and prepares the environment for visualization.

**Raises:**

- `FileNotFoundError`: If any of the provided file paths do not exist.
- `ValueError`: If the provided files are not `.py` files.

**Example Usage:**

```python
from gensphere.visualizer import Visualizer

viz = Visualizer(
    yaml_file='workflow.yaml',
    functions_filepath='functions.py',
    structured_output_schema_filepath='schemas.py',
    address='127.0.0.1',
    port=8050
)
```

### Methods

#### `start_visualization`

```python
def start_visualization(self):
```

**Description:**

Starts the Dash application for visualizing the GenSphere workflow. The application provides an interactive interface where nodes are displayed graphically, and users can click on nodes to view detailed information such as parameters, outputs, functions, and schemas.

**Features:**

- **Graph Visualization:** Uses Cytoscape to render the workflow graph.
- **Interactive Nodes:** Clicking on a node displays detailed information.
- **Legend:** Includes a legend explaining node types and edge styles.
- **Dynamic Loading:** Users can input a different YAML file path and reload the graph.

**Example Usage:**

```python
viz.start_visualization()
```

After running this method, navigate to `http://127.0.0.1:8050` in your web browser to view the visualization.

**Notes:**

- Ensure that the YAML file and any referenced functions or schemas are correctly specified.
- The visualization runs a local web server; make sure the specified `address` and `port` are accessible.

---

## Hub

**Module:** `hub.py`

The `Hub` class provides an interface to interact with the GenSphere Hub platform. It allows users to push workflows to the hub, pull workflows from the hub, and check the number of times a workflow has been pulled.

### Class Definition

```python
class Hub:
    def __init__(self, yaml_file=None, functions_file=None, schema_file=None, api_base_url='http://genspherehub.us-east-1.elasticbeanstalk.com/'):
        # Initialization code

    def push(self, push_name=None):
        # Pushes the workflow to the GenSphere Hub

    def pull(self, push_id, save_to_disk=True, yaml_filename=None, functions_filename=None, schema_filename=None, download_path="."):
        # Pulls a workflow from the GenSphere Hub

    def count_pulls(self, push_id):
        # Retrieves the total number of times a push has been pulled
```

### Constructor

```python
def __init__(self, yaml_file=None, functions_file=None, schema_file=None, api_base_url='http://genspherehub.us-east-1.elasticbeanstalk.com/'):
```

**Parameters:**

- `yaml_file` (_str_, optional): Path to the YAML file to be pushed.
- `functions_file` (_str_, optional): Path to the functions file to be pushed.
- `schema_file` (_str_, optional): Path to the schema file to be pushed.
- `api_base_url` (_str_, optional): Base URL for the GenSphere Hub API.

**Description:**

Initializes the `Hub` instance with the provided file paths and API base URL. Prepares the instance for pushing and pulling workflows to and from the GenSphere Hub platform.

**Example Usage:**

```python
from gensphere.hub import Hub

hub = Hub(
    yaml_file='workflow.yaml',
    functions_file='functions.py',
    schema_file='schemas.py'
)
```

### Methods

#### `push`

```python
def push(self, push_name=None):
```

**Parameters:**

- `push_name` (_str_, optional): A descriptive name for the workflow being pushed.

**Returns:**

- `result` (_dict_): A dictionary containing the `push_id` and a list of uploaded files.

**Description:**

Pushes the specified workflow files to the GenSphere Hub. Validates the YAML file for consistency before pushing. The `push_id` returned can be used to pull the workflow or check its pull count.

**Raises:**

- `ValueError`: If no `yaml_file` is provided or if the functions or schema files are not `.py` files.
- `Exception`: If validation fails or if an error occurs during the push.

**Example Usage:**

```python
result = hub.push(push_name='My Awesome Workflow')
push_id = result.get('push_id')
print(f"Workflow pushed with push_id: {push_id}")
```

#### `pull`

```python
def pull(self, push_id, save_to_disk=True, yaml_filename=None, functions_filename=None, schema_filename=None, download_path="."):
```

**Parameters:**

- `push_id` (_str_): The `push_id` of the workflow to pull.
- `save_to_disk` (_bool_, optional): If `True`, saves the pulled files to disk (default: `True`).
- `yaml_filename` (_str_, optional): Custom filename for the YAML file.
- `functions_filename` (_str_, optional): Custom filename for the functions file.
- `schema_filename` (_str_, optional): Custom filename for the schema file.
- `download_path` (_str_, optional): Directory to save the pulled files (default: `"."`).

**Returns:**

- `files_content` (_dict_): A dictionary containing the contents of the pulled files.

**Description:**

Pulls a workflow from the GenSphere Hub using the provided `push_id`. Optionally saves the files to disk with custom filenames. Ensures that existing files are not overwritten by appending a counter if necessary.

**Raises:**

- `Exception`: If an error occurs during the pull operation.

**Example Usage:**

```python
files = hub.pull(
    push_id=push_id,
    save_to_disk=True,
    yaml_filename='downloaded_workflow.yaml',
    functions_filename='downloaded_functions.py',
    schema_filename='downloaded_schemas.py'
)
```

#### `count_pulls`

```python
def count_pulls(self, push_id):
```

**Parameters:**

- `push_id` (_str_): The `push_id` of the workflow to check.

**Returns:**

- `pull_count` (_int_): The total number of times the workflow has been pulled.

**Description:**

Retrieves the total number of times a workflow has been pulled from the GenSphere Hub using the provided `push_id`.

**Raises:**

- `Exception`: If an error occurs during the request.

**Example Usage:**

```python
pull_count = hub.count_pulls(push_id=push_id)
print(f"The workflow has been pulled {pull_count} times.")
```

---

## Utility Functions

### parse_yaml

**Module:** `graph_builder.py`

```python
def parse_yaml(yaml_file):
```

**Parameters:**

- `yaml_file` (_str_): Path to the YAML file to parse.

**Returns:**

- `data` (_dict_): Parsed YAML data.

**Description:**

Parses a YAML file and returns its content as a dictionary. Validates the existence of the file and handles parsing errors.

**Raises:**

- `FileNotFoundError`: If the YAML file does not exist.
- `yaml.YAMLError`: If an error occurs during YAML parsing.

**Example Usage:**

```python
data = parse_yaml('workflow.yaml')
```

---

### extract_referenced_nodes

**Module:** `graph_builder.py`

```python
def extract_referenced_nodes(template_str):
```

**Parameters:**

- `template_str` (_str_): A templated string containing references to other nodes (e.g., `"{{ node.output }}"`).

**Returns:**

- `referenced_nodes` (_Set[str]_): A set of referenced node names.

**Description:**

Extracts all referenced node names from a templated string using regular expressions. Useful for identifying dependencies between nodes in a workflow.

**Example Usage:**

```python
template_str = "{{ node1.output }} and {{ node2.output }}"
referenced_nodes = extract_referenced_nodes(template_str)
# referenced_nodes will be {'node1', 'node2'}
```

---

### traverse_node_fields

**Module:** `graph_builder.py`

```python
def traverse_node_fields(node_value):
```

**Parameters:**

- `node_value` (_Union[str, dict, list]_): The node value to traverse.

**Returns:**

- `referenced_nodes` (_Set[str]_): A set of referenced node names found within the node value.

**Description:**

Recursively traverses a node's fields to find all referenced node names. Handles strings, dictionaries, and lists. Used to identify all dependencies for a node.

**Example Usage:**

```python
node_params = {
    'param1': '{{ node1.output }}',
    'param2': {
        'subparam': '{{ node2.output }}'
    }
}
referenced_nodes = traverse_node_fields(node_params)
# referenced_nodes will be {'node1', 'node2'}
```

---

### identify_and_style_entrypoints_outputs

**Module:** `graph_builder.py`

```python
def identify_and_style_entrypoints_outputs(elements):
```

**Parameters:**

- `elements` (_list_): List of Cytoscape elements (nodes and edges).

**Returns:**

- `elements` (_list_): Updated list of Cytoscape elements with styled entrypoints and output nodes.

**Description:**

Identifies entrypoint nodes (nodes with no incoming edges) and output nodes (nodes with no outgoing edges) in the workflow graph and styles them accordingly for visualization purposes.

**Example Usage:**

```python
elements = identify_and_style_entrypoints_outputs(elements)
```

---

### build_graph_data

**Module:** `graph_builder.py`

```python
def build_graph_data(yaml_file):
```

**Parameters:**

- `yaml_file` (_str_): Path to the YAML file defining the workflow.

**Returns:**

- `elements` (_list_): List of Cytoscape elements (nodes and edges) representing the workflow graph.

**Description:**

Builds graph data compatible with Cytoscape from a YAML workflow definition. It processes nodes and edges, identifies dependencies, and prepares the data for visualization.

**Raises:**

- `ValueError`: If a node lacks a name or if there are duplicate node names.

**Example Usage:**

```python
elements = build_graph_data('workflow.yaml')
```

---

## Additional Information

These classes and functions are integral to GenSphere's capabilities for visualizing workflows and interacting with the GenSphere Hub platform. Understanding them allows users to extend functionality, troubleshoot issues, and fully leverage GenSphere's features.

---

**Note:** When using the `Visualizer` and `Hub` classes:

- Ensure that all file paths provided are correct and that files exist.
- Handle exceptions appropriately, especially when dealing with network requests in the `Hub` class.

---

## Conclusion

This API reference provides detailed insights into the classes and functions used for visualizing GenSphere workflows and interacting with the GenSphere Hub. With this knowledge, you can:

- Visualize your workflows to better understand execution flow and dependencies.
- Share and retrieve workflows from the GenSphere Hub platform.
- Extend and customize visualization and hub interactions according to your needs.

For more examples and usage instructions, refer to the [User Guide](../user_guide/workflows.md) and [Tutorials](../tutorials/quickstart_tutorial.md).

---

If you have any questions or need further assistance, please refer to the [FAQ](../faq.md) or reach out on our [GitHub Issues](https://github.com/octopus2023-inc/gensphere/issues) page.

# End of API Reference Sections

---

You're now equipped with detailed knowledge of GenSphere's visualization and hub capabilities. Happy coding!