## 3. Nesting Workflows

GenSphere allows you to create modular and reusable workflows by nesting workflows within each other. This is achieved using the `yml_flow` node type. Nesting workflows can help you organize complex tasks and promote code reuse.

### 3.1 Understanding YML Flow Nodes

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

### 3.2 Creating Nested Workflows

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

### 3.3 Passing Parameters to Nested Workflows

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

### 3.4 Accessing Outputs from Nested Workflows

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

### 3.5 Composing the Combined Workflow

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
