# API Reference

This section provides detailed documentation of the core classes and utility functions used in GenSphere, specifically focusing on the `genflow.py` and `yaml_utils.py` modules.

---

## Core Classes

- [GenFlow](#genflow)
- [Node](#node)
- [YamlCompose](#yamlcompose)

---

### GenFlow

**Module:** `genflow.py`

The `GenFlow` class is responsible for parsing YAML workflow definitions, constructing an execution graph, and executing nodes in the correct order. It manages the overall workflow execution process.

#### Class Definition

```python
class GenFlow:
    def __init__(self, yaml_file, functions_filepath=None, structured_output_schema_filepath=None):
        # Initialization code

    def parse_yaml(self):
        # Parses the YAML data and constructs nodes

    def build_graph(self):
        # Builds the execution graph

    def run(self):
        # Executes the nodes in topological order
```

#### Constructor

```python
def __init__(self, yaml_file, functions_filepath=None, structured_output_schema_filepath=None):
```

**Parameters:**

- `yaml_file` (_str_): Path to the main YAML file defining the workflow.
- `functions_filepath` (_str_, optional): Path to the Python file containing custom function definitions.
- `structured_output_schema_filepath` (_str_, optional): Path to the Python file containing structured output schemas.

**Description:**

Initializes the `GenFlow` instance by loading the YAML data and preparing the environment for execution. It verifies the validity of provided file paths and ensures that the necessary files are accessible.

**Raises:**

- `FileNotFoundError`: If the provided `functions_filepath` or `structured_output_schema_filepath` does not exist.
- `ValueError`: If the provided file paths are not `.py` files.

#### Methods

##### `parse_yaml`

```python
def parse_yaml(self):
```

**Description:**

Parses the YAML data from the main workflow file and constructs the nodes for execution. It also checks for the presence of nested workflows (`yml_flow` nodes) and composes them using `YamlCompose` if necessary. Validates the YAML file for consistency before parsing.

**Raises:**

- `Exception`: If the YAML file fails consistency checks.

**Example Usage:**

```python
flow = GenFlow('workflow.yaml', 'functions.py', 'schemas.py')
flow.parse_yaml()
```

##### `build_graph`

```python
def build_graph(self):
```

**Description:**

Builds a directed acyclic graph (DAG) representing the execution order of nodes based on their dependencies. It adds nodes and edges to the graph according to the dependencies identified during parsing.

**Raises:**

- `ValueError`: If the graph contains cycles or if a node depends on an undefined node or variable.

**Example Usage:**

```python
flow.build_graph()
```

##### `run`

```python
def run(self):
```

**Description:**

Executes the nodes in the order determined by the topological sort of the execution graph. It renders the parameters for each node using the outputs of previously executed nodes and handles iterative execution for nodes processing lists.

**Raises:**

- `Exception`: If there are cycles in the graph or if an error occurs during node execution.

**Example Usage:**

```python
flow.run()
```

After execution, the outputs from each node are stored in the `outputs` attribute of the `GenFlow` instance.

---

### Node

**Module:** `genflow.py`

The `Node` class represents an individual operation or step within the workflow. It encapsulates the logic required to execute that step, including parameter rendering and function execution.

#### Class Definition

```python
class Node:
    def __init__(self, node_data):
        # Initialization code

    def set_flow(self, flow):
        # Sets reference to the GenFlow instance

    def get_dependencies(self, node_names):
        # Retrieves the dependencies of the node

    def render_params(self, outputs, env):
        # Renders the parameters using previous outputs

    def execute(self, params):
        # Executes the node based on its type and parameters
```

#### Constructor

```python
def __init__(self, node_data):
```

**Parameters:**

- `node_data` (_dict_): Dictionary containing the node's configuration from the YAML file.

**Description:**

Initializes the `Node` instance with the given configuration. It extracts essential information such as the node's name, type, outputs, and parameters.

#### Methods

##### `set_flow`

```python
def set_flow(self, flow):
```

**Parameters:**

- `flow` (_GenFlow_): Reference to the `GenFlow` instance managing the workflow execution.

**Description:**

Sets the reference to the `GenFlow` instance, allowing the node to access shared resources and configurations during execution.

##### `get_dependencies`

```python
def get_dependencies(self, node_names):
```

**Parameters:**

- `node_names` (_Iterable[str]_): Iterable of all node names in the workflow.

**Returns:**

- `dependencies` (_Set[str]_): Set of node names that the current node depends on.

**Description:**

Analyzes the node's parameters to determine which other nodes it depends on. This is used to build the execution graph and ensure correct execution order.

**Example Usage:**

```python
dependencies = node.get_dependencies(flow.nodes.keys())
```

##### `render_params`

```python
def render_params(self, outputs, env):
```

**Parameters:**

- `outputs` (_dict_): Outputs from previously executed nodes.
- `env` (_jinja2.Environment_): Jinja2 environment used for templating.

**Returns:**

- `rendered_params` (_dict_ or _list of dicts_): Parameters with values rendered using the outputs of previous nodes.

**Description:**

Renders the node's parameters by substituting placeholders with actual values from previous outputs. Supports handling of indexed parameters and lists for iterative processing.

**Raises:**

- `ValueError`: If a referenced variable is not found or is not iterable when expected.

##### `execute`

```python
def execute(self, params):
```

**Parameters:**

- `params` (_dict_): Parameters to be used for the node execution.

**Returns:**

- `outputs` (_dict_): Dictionary of outputs produced by the node execution.

**Description:**

Executes the node based on its type:

- For `function_call` nodes, it executes a Python function.
- For `llm_service` nodes, it interacts with an LLM service like OpenAI.

Delegates to specific execution methods depending on the node type.

**Raises:**

- `NotImplementedError`: If the node type is not supported.
- `Exception`: If an error occurs during execution.

**Example Usage:**

```python
outputs = node.execute(rendered_params)
```

---

### YamlCompose

**Module:** `yaml_utils.py`

The `YamlCompose` class is responsible for composing multiple YAML workflow files into a single unified workflow. It resolves references to nested workflows (`yml_flow` nodes) and adjusts node names and parameters to ensure uniqueness and consistency.

#### Class Definition

```python
class YamlCompose:
    def __init__(self, yaml_file, functions_filepath, structured_output_schema_filepath):
        # Initialization code

    def compose(self, save_combined_yaml=False, output_file='combined.yaml'):
        # Starts the composition process and returns the combined YAML data
```

#### Constructor

```python
def __init__(self, yaml_file, functions_filepath, structured_output_schema_filepath):
```

**Parameters:**

- `yaml_file` (_str_): Path to the root YAML file to be composed.
- `functions_filepath` (_str_): Path to the Python file containing custom functions.
- `structured_output_schema_filepath` (_str_): Path to the Python file containing structured output schemas.

**Description:**

Initializes the `YamlCompose` instance and prepares for the composition process by validating the provided file paths.

**Raises:**

- `FileNotFoundError`: If the provided file paths do not exist.
- `ValueError`: If the provided file paths are not `.py` files.

#### Methods

##### `compose`

```python
def compose(self, save_combined_yaml=False, output_file='combined.yaml'):
```

**Parameters:**

- `save_combined_yaml` (_bool_, optional): If `True`, saves the combined YAML data to a file.
- `output_file` (_str_, optional): Filename to save the combined YAML data.

**Returns:**

- `combined_data` (_dict_): The combined YAML data after composition.

**Description:**

Starts the composition process by recursively processing the root YAML file and any nested sub-flows. Adjusts node names and parameter references to ensure uniqueness across the combined workflow.

**Raises:**

- `Exception`: If validation fails during composition.

**Example Usage:**

```python
composer = YamlCompose('main_workflow.yaml', 'functions.py', 'schemas.py')
combined_yaml_data = composer.compose(save_combined_yaml=True, output_file='combined.yaml')
```

After composition, the combined YAML file can be executed as a single workflow.

---

## Utility Functions

This section documents the utility functions used within GenSphere, primarily for internal processing and validation.

---

### get_function_schema

**Module:** `genflow.py`

```python
def get_function_schema(func):
```

**Parameters:**

- `func` (_function_): The Python function object to generate a schema for.

**Returns:**

- `function_def` (_dict_): A dictionary representing the function definition, including name, description, and parameters.

**Description:**

Generates a schema for a given function by inspecting its signature and docstring. This schema is used for OpenAI's function calling feature in LLM service nodes. It ensures that the function parameters are properly typed and documented.

**Raises:**

- `ValueError`: If a parameter lacks a type annotation or if the function lacks a docstring.

**Example Usage:**

Used internally when preparing function definitions for OpenAI's function calling.

---

### validate_yaml

**Module:** `yaml_utils.py`

```python
def validate_yaml(
    yaml_file,
    functions_filepath=None,
    structured_output_schema_filepath=None,
    parent_node_names=None,
    visited_files=None,
    parent_params=None,
    parent_node_outputs=None
):
```

**Parameters:**

- `yaml_file` (_str_): Path to the YAML file being validated.
- `functions_filepath` (_str_, optional): Path to the functions file.
- `structured_output_schema_filepath` (_str_, optional): Path to the schemas file.
- `parent_node_names` (_Set[str]_, optional): Set of node names from the parent flow.
- `visited_files` (_Set[str]_, optional): Set of visited YAML files to prevent circular references.
- `parent_params` (_Set[str]_, optional): Set of parameter names passed from the parent flow.
- `parent_node_outputs` (_Dict[str, List[str]]_, optional): Dictionary of node outputs from parent flows.

**Returns:**

- `validated` (_bool_): `True` if validation passes, `False` otherwise.
- `error_msgs` (_List[str]_): List of error messages encountered during validation.
- `node_outputs` (_Dict[str, List[str]]_): Dictionary of node outputs in the current flow.

**Description:**

Validates a YAML workflow file and any associated sub-flows for consistency and correctness. Checks for issues such as:

- Missing required fields (`name`, `type`).
- Duplicate node names.
- Undefined or duplicate outputs.
- References to undefined nodes or outputs.
- Cycles in the execution graph.
- Validity of functions and schemas.

**Raises:**

- `FileNotFoundError`: If referenced files do not exist.
- `ValueError`: If the YAML structure is invalid.

**Example Usage:**

Used internally before executing or composing workflows to ensure they are valid.

---

### collect_referenced_nodes_and_outputs

**Module:** `yaml_utils.py`

```python
def collect_referenced_nodes_and_outputs(params):
```

**Parameters:**

- `params` (_dict_): Parameters dictionary from a node.

**Returns:**

- `referenced_nodes_outputs` (_Set[Tuple[str, str]]_): A set of tuples containing referenced node names and outputs.

**Description:**

Analyzes the parameters of a node to identify all referenced nodes and their outputs, which is essential for validating dependencies and ensuring that all references are valid.

---

### collect_used_params

**Module:** `yaml_utils.py`

```python
def collect_used_params(yaml_data):
```

**Parameters:**

- `yaml_data` (_dict_): The YAML data of a workflow.

**Returns:**

- `used_params` (_Set[str]_): A set of parameter names used within the workflow.

**Description:**

Collects all parameter names that are used in the workflow, particularly in the context of nested workflows (`yml_flow` nodes). This helps in validating that all required parameters are provided.

---

### collect_referenced_params

**Module:** `yaml_utils.py`

```python
def collect_referenced_params(params):
```

**Parameters:**

- `params` (_dict_): Parameters dictionary from a node.

**Returns:**

- `referenced_params` (_Set[str]_): A set of parameter names referenced in the parameters.

**Description:**

Identifies all parameter names that are referenced within the node's parameters, usually in templated strings. This is used to ensure that all referenced parameters are defined.

---

### collect_referenced_nodes

**Module:** `yaml_utils.py`

```python
def collect_referenced_nodes(params):
```

**Parameters:**

- `params` (_dict_): Parameters dictionary from a node.

**Returns:**

- `referenced_nodes` (_Set[str]_): A set of node names referenced in the parameters.

**Description:**

Identifies all node names that are referenced within the node's parameters. This is crucial for building the execution graph and determining the correct execution order.

---

### load_yaml_file

**Module:** `yaml_utils.py`

```python
def load_yaml_file(yaml_file):
```

**Parameters:**

- `yaml_file` (_str_): Path to the YAML file to load.

**Returns:**

- `data` (_dict_): The loaded YAML data.

**Description:**

Loads the YAML data from a file and handles parsing errors. Ensures that the file exists and contains valid YAML.

**Raises:**

- `FileNotFoundError`: If the YAML file does not exist.
- `ValueError`: If there is an error parsing the YAML file.

---

### has_yml_flow_nodes

**Module:** `yaml_utils.py`

```python
def has_yml_flow_nodes(yaml_data):
```

**Parameters:**

- `yaml_data` (_dict_): The YAML data of a workflow.

**Returns:**

- `bool`: `True` if the workflow contains any `yml_flow` nodes, `False` otherwise.

**Description:**

Checks whether the given YAML data contains any nested workflows (`yml_flow` nodes). This helps determine if composition is necessary before execution.

---

### get_base_output_name

**Module:** `yaml_utils.py`

```python
def get_base_output_name(output_reference):
```

**Parameters:**

- `output_reference` (_str_): A string representing an output reference (e.g., `'countries_list[i]'`).

**Returns:**

- `base_output_name` (_str_): The base output name extracted from the reference.

**Description:**

Extracts the base output name from a complex output reference that may include indexing or attribute access. Used during validation to identify the actual outputs being referenced.

---

## Additional Information

These utility functions are primarily used internally by GenSphere to process and validate workflows. Understanding them can be helpful for advanced users who wish to extend or debug the framework.

---

**Note:** When developing custom functions or schemas for use in GenSphere workflows, ensure that:

- Functions have proper docstrings and type annotations.
- Schemas are defined using Pydantic models.
- Functions and schemas are placed in the files specified when initializing `GenFlow` or `YamlCompose`.

---

## Conclusion

This API reference provides detailed insights into the core classes and utility functions of GenSphere's workflow execution engine. With this knowledge, developers can better understand how GenSphere processes workflows, handles dependencies, and executes tasks.

For more examples and usage instructions, refer to the [User Guide](../user_guide/workflows.md) and [Tutorials](../tutorials/tutorial.md).

---

If you have any questions or need further assistance, reach out on our [GitHub Issues](https://github.com/octopus2023-inc/gensphere/issues) page.
