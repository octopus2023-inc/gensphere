# User Guide

Welcome back to the GenSphere User Guide! In this section, we'll continue exploring the advanced features of GenSphere, focusing on nesting workflows, visualization, execution, and using the GenSphere Hub.

---

## Table of Contents

1. [Nesting Workflows](#1-nesting-workflows)
2. [Visualization](#2-visualization)
3. [Execution](#3-execution)
4. [Using the GenSphere Hub](#4-using-the-gensphere-hub)

---

## 1. Nesting Workflows

GenSphere allows you to create modular and reusable workflows by nesting workflows within each other. This is achieved using the `yml_flow` node type. Nesting workflows can help you organize complex tasks and promote code reuse.

### 1.1 Understanding YML Flow Nodes

A `yml_flow` node refers to another YAML workflow file. When the main workflow is executed, GenSphere will incorporate the nested workflow, resolving dependencies and combining them into a single execution graph.

**Example:**

```yaml
# main_workflow.yaml

nodes:
  - name: data_collection
    type: yml_flow
    yml_file: data_collection_workflow.yaml
    params:
      start_date: '2023-01-01'
      end_date: '2023-01-31'
    outputs:
      - collected_data

  - name: data_analysis
    type: function_call
    function: analyze_data_function
    params:
      data: '{{ data_collection.collected_data }}'
    outputs:
      - analysis_results
```

In this example:

- **`data_collection`**: A `yml_flow` node that references `data_collection_workflow.yaml`.
- **Parameters**: `start_date` and `end_date` are passed to the nested workflow.
- **Outputs**: `collected_data` is an output from the nested workflow used in the main workflow.

### 1.2 Creating Nested Workflows

To create a nested workflow:

1. **Define the Sub-Workflow**: Create a separate YAML file (e.g., `data_collection_workflow.yaml`) with its own nodes.

   ```yaml
   # data_collection_workflow.yaml

   nodes:
     - name: fetch_data
       type: function_call
       function: fetch_data_function
       params:
         start_date: '{{ start_date }}'
         end_date: '{{ end_date }}'
       outputs:
         - raw_data

     - name: process_data
       type: function_call
       function: process_data_function
       params:
         data: '{{ fetch_data.raw_data }}'
       outputs:
         - processed_data
   ```

2. **Reference the Sub-Workflow**: In your main workflow, use a `yml_flow` node to include the sub-workflow.

### 1.3 Passing Parameters to Nested Workflows

Parameters can be passed to nested workflows using the `params` field in the `yml_flow` node. These parameters can then be used within the nested workflow.

**Example:**

```yaml
# main_workflow.yaml

nodes:
  - name: sub_workflow
    type: yml_flow
    yml_file: sub_workflow.yaml
    params:
      param1: '{{ main_param }}'
```

### 1.4 Accessing Outputs from Nested Workflows

Outputs specified in the `outputs` field of the `yml_flow` node are made available to the main workflow.

**Example:**

```yaml
- name: data_collection
  type: yml_flow
  yml_file: data_collection_workflow.yaml
  outputs:
    - collected_data
```

In subsequent nodes, you can reference `data_collection.collected_data`.

### 1.5 Composing the Combined Workflow

Use the `YamlCompose` class to combine the main workflow and nested workflows into a single executable workflow.

**Example:**

```python
from gensphere.yaml_utils import YamlCompose

composer = YamlCompose(
    yaml_file='main_workflow.yaml',
    functions_filepath='functions.py',
    structured_output_schema_filepath='schemas.py'
)
combined_yaml_data = composer.compose(save_combined_yaml=True, output_file='combined.yaml')
```

---

## 2. Visualization

Visualizing your workflow helps you understand the execution flow and dependencies between nodes. GenSphere provides a visualization tool to render your workflow as an interactive graph.

### 2.1 Using the Visualizer

The `Visualizer` class in GenSphere allows you to visualize your workflow.

**Example:**

```python
from gensphere.visualizer import Visualizer

viz = Visualizer(
    yaml_file='combined.yaml',
    functions_file='functions.py',
    schema_file='schemas.py',
    address='127.0.0.1',
    port=8050
)
viz.start_visualization()
```

### 2.2 Features of the Visualizer

- **Interactive Graph**: Nodes are displayed as a graph where you can zoom in/out.
- **Node Details**: Click on a node to see details such as inputs, outputs, functions, and schemas.
- **Execution Flow**: Visualize the dependencies and execution order.

### 2.3 Running the Visualizer

When you run `viz.start_visualization()`, the visualizer starts a local web server. Open your browser and navigate to `http://127.0.0.1:8050` (or the specified address and port) to view the visualization.

**Note:** If you're running in an environment like Google Colab, you might need to set up port forwarding or use a different method to access the visualization.

---

## 3. Execution

Executing workflows in GenSphere is straightforward using the `GenFlow` class. This section explains how to execute your workflow and handle outputs.

### 3.1 Setting Up the Environment

Ensure that:

- All required environment variables (e.g., API keys) are set.
- All necessary files (`yaml`, `functions.py`, `schemas.py`) are available.

### 3.2 Executing the Workflow

Use the `GenFlow` class to execute your workflow.

**Example:**

```python
from gensphere.genflow import GenFlow

flow = GenFlow(
    yaml_file='combined.yaml',
    functions_filepath='functions.py',
    structured_output_schema_filepath='schemas.py'
)
flow.parse_yaml()
flow.run()
```

### 3.3 Accessing Outputs

After execution, outputs from each node are accessible via the `outputs` attribute.

**Example:**

```python
# Access all outputs
outputs = flow.outputs

# Access specific node outputs
data_collection_output = outputs.get('data_collection').get('collected_data')

# Print the outputs
print("Collected Data:")
print(data_collection_output)
```

### 3.4 Handling Exceptions

If an error occurs during execution:

- Check the log files for detailed error messages.
- Ensure that all referenced nodes, functions, and schemas exist.
- Verify that all parameters are correctly specified.

### 3.5 Logging

GenSphere uses Python's logging module to log execution details.

- **Logging Levels**: Adjust logging levels as needed.
  ```python
  import logging
  logging.getLogger('gensphere').setLevel(logging.DEBUG)
  ```
- **Log File**: By default, logs may be written to `app.log` or the console.

### 3.6 Execution Flow

The execution order of nodes is determined by their dependencies:

- Nodes with no dependencies are executed first.
- Nodes are executed after all their dependencies have completed.

---

## 4. Using the GenSphere Hub

The GenSphere Hub is a platform that allows you to share your workflows with the community and access workflows shared by others.

### 4.1 Pushing Workflows to the Hub

To share your workflow, use the `Hub` class to push your files to the platform.

**Example:**

```python
from gensphere.hub import Hub

hub = Hub(
    yaml_file='combined.yaml',
    functions_file='functions.py',
    schema_file='schemas.py'
)

result = hub.push(push_name='My Awesome Workflow')
push_id = result.get('push_id')
print(f"Your workflow has been pushed with push_id: {push_id}")
```

**Parameters:**

- **`push_name`**: A descriptive name for your workflow.
- **`yaml_file`**, **`functions_file`**, **`schema_file`**: Paths to your workflow files.

### 4.2 Pulling Workflows from the Hub

To use a workflow shared by someone else, you can pull it using the `push_id`.

**Example:**

```python
hub = Hub()
hub.pull(
    push_id='abcd1234-5678-90ef-ghij-klmnopqrstuv',
    yaml_filename='downloaded_workflow.yaml',
    functions_filename='downloaded_functions.py',
    schema_filename='downloaded_schemas.py',
    save_to_disk=True
)
```

### 4.3 Counting Pulls

You can check how many times your workflow has been pulled.

**Example:**

```python
total_pulls = hub.count_pulls(push_id=push_id)
print(f"Your workflow has been pulled {total_pulls} times.")
```

### 4.4 Deleting a Workflow from the Hub

If you need to remove your workflow from the Hub, you can delete it.

**Example:**

```python
hub.delete_push(push_id=push_id)
print("Your workflow has been deleted from the Hub.")
```

**Note:** Ensure you have the necessary permissions to delete the workflow.

### 4.5 Best Practices for Sharing Workflows

- **Descriptive Names**: Use clear and descriptive names for your workflows.
- **Documentation**: Include comments or documentation within your functions and schemas to help others understand your workflow.
- **Dependencies**: Ensure all dependencies are included or documented.

### 4.6 Privacy and Security

- **Sensitive Data**: Do not include API keys or sensitive information in your shared workflows.
- **Licensing**: Respect licensing agreements and include appropriate licenses if necessary.

---

## Conclusion

You've now learned how to:

- **Nest Workflows**: Create modular and reusable workflows using `yml_flow` nodes.
- **Visualize Workflows**: Use the `Visualizer` to understand and debug your workflows.
- **Execute Workflows**: Run your workflows using the `GenFlow` class and handle outputs.
- **Use the GenSphere Hub**: Share your workflows with the community and access others' workflows.

---

## Additional Resources

- **[GenSphere GitHub Repository](https://github.com/octopus2023-inc/gensphere)**
- **[GenSphere Documentation](../index.md)**
- **[Community Forum](https://community.gensphere.dev)**
- **[Issue Tracker](https://github.com/octopus2023-inc/gensphere/issues)**

---

## Feedback

We value your feedback! If you have suggestions, questions, or need help, please reach out on our [GitHub Issues](https://github.com/octopus2023-inc/gensphere/issues) page or join the community forum.

# End of User Guide Sections

---

You're now equipped with the knowledge to fully utilize GenSphere's capabilities. Happy coding!