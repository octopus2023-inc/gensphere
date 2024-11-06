## 2. Functions and Schemas

In GenSphere, you can define custom functions and schemas to extend the functionality of your workflows.

### 2.1 Functions

Custom functions are Python functions defined in a `.py` file that you specify when running your workflow. These functions can be used in **function_call** nodes or as tools in **llm_service** nodes.

#### Defining Functions

- Functions must return a dictionary whose keys match the `outputs` defined in the YAML node.
- All parameters must be type-annotated.
- Include docstrings to describe the function's purpose, parameters, and return values.

**Example (`functions.py`):**

```python
def process_data_function(data: str) -> dict:
    """
    Processes the input data.

    Args:
        data (str): The data to process.

    Returns:
        dict: A dictionary with 'processed_data' as key.
    """
    # Your processing logic here
    processed_data = data.upper()  # Example processing
    return {'processed_data': processed_data}
```

#### Using Functions in Nodes

**Example YAML Node:**

```yaml
- name: process_data
  type: function_call
  function: process_data_function
  params:
    data: '{{ read_data.raw_data }}'
  outputs:
    - processed_data
```

### 2.2 Schemas

Schemas are used to define structured outputs for language model responses using Pydantic models.

#### Defining Schemas

Create a `.py` file (e.g., `schemas.py`) with Pydantic models representing the expected structure of your data.

**Example (`schemas.py`):**

```python
from pydantic import BaseModel, Field
from typing import List

class Item(BaseModel):
    id: int = Field(..., description="The unique identifier of the item.")
    name: str = Field(..., description="The name of the item.")
    description: str = Field(..., description="A brief description of the item.")

class ItemList(BaseModel):
    items: List[Item]
```

#### Using Schemas in Nodes

Use the `structured_output_schema` field in an **llm_service** node to specify the schema.

**Example YAML Node:**

```yaml
- name: extract_items
  type: llm_service
  service: openai
  model: "gpt-4"
  structured_output_schema: ItemList
  params:
    prompt: |
      Extract item information from the following text:
      {{ source_text }}
  outputs:
    - extracted_items
```

**Key Points:**

- The `structured_output_schema` value should match the class name in your schema file.
- The language model will attempt to produce output that conforms to the specified schema.

#### Accessing Structured Outputs

After execution, the output will be an instance of the schema class. You can access the data using standard attribute access.

**Example:**

```python
items = flow.outputs['extract_items']['extracted_items']
for item in items.items:
    print(f"Item ID: {item.id}, Name: {item.name}")
```

---
