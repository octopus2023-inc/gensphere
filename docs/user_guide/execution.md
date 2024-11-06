## 7. Execution

Executing workflows in GenSphere is straightforward using the `GenFlow` class. This section explains how to execute your workflow and handle outputs.

### 7.1 Setting Up the Environment

Ensure that:

- All required environment variables (e.g., API keys) are set.
- All necessary files (`yaml`, `functions.py`, `schemas.py`) are available.

### 7.2 Executing the Workflow

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

### 7.3 Accessing Outputs

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

### 7.4 Handling Exceptions

If an error occurs during execution:

- Check the log files for detailed error messages.
- Ensure that all referenced nodes, functions, and schemas exist.
- Verify that all parameters are correctly specified.

### 7.5 Logging

GenSphere uses Python's logging module to log execution details.

- **Logging Levels**: Adjust logging levels as needed.
  ```python
  import logging
  logging.getLogger('gensphere').setLevel(logging.DEBUG)
  ```
- **Log File**: By default, logs may be written to `app.log` or the console.

### 7.6 Execution Flow

The execution order of nodes is determined by their dependencies:

- Nodes with no dependencies are executed first.
- Nodes are executed after all their dependencies have completed.

---
