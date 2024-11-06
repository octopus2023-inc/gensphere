# User Guide

Welcome to the GenSphere User Guide! This section provides detailed information on how to use GenSphere to build and execute complex AI workflows. Whether you're a beginner or an experienced developer, this guide will help you understand the core concepts and features of GenSphere.

---

## Table of Contents

1. [Workflows](#1-workflows)
2. [Functions and Schemas](#2-functions-and-schemas)
3. [Integrations](#3-integrations)
4. [Lists and Iterables](#4-lists-and-iterables)

---

## 1. Workflows

GenSphere uses **YAML files** to define workflows that orchestrate the execution of functions, language model services, and nested workflows. Understanding how to structure and write these YAML files is essential to leveraging the full power of GenSphere.

### 1.1 Structure of a Workflow

A GenSphere workflow YAML file consists of a list of **nodes**, each representing a step in the workflow. Here's the basic structure:

```yaml
# example_workflow.yaml

nodes:
  - name: node_name
    type: node_type # can be either 'function_call','llm_service' of 'yml_flow'
    params:
      param1: value1
      param2: value2
    outputs:
      - output1
      - output2
```
There are additional fields needed depending on the 'type' field.

### 1.2 Node Types

There are three primary node types in GenSphere:

1. **Function Call Nodes** (`function_call`): Execute Python functions.
2. **LLM Service Nodes** (`llm_service`): Interact with language model APIs.
3. **YML Flow Nodes** (`yml_flow`): Nest other YAML workflows.

#### Function Call Nodes

Used to execute custom Python functions defined in a separate `.py` file.

**Example:**

```yaml
- name: process_data
  type: function_call
  function: process_data_function
  params:
    data: '{{ previous_node.output }}'
  outputs:
    - processed_data
```

The function `process_data_function` should be defined on a separate `.py` file that contains all functions that you will use. We don't set the path of this `.py` file
directly in the YAML, but pass it as na argument to GenFlow when executing the graph (as explained below).

#### LLM Service Nodes

Used to interact with language model services like OpenAI's GPT models.

**Example:**

```yaml
- name: generate_summary
  type: llm_service
  service: openai
  model: "gpt-4"
  tools: 
    - COMPOSIO.composio_tool_name
    - LANGCHAIN.langchain_tool_name
    - custom_function
  params:
    prompt: |
      Summarize the following data:
      {{ process_data.processed_data }}
  outputs:
    - summary
```
In the example above, we are making na API call to the `chat_completions` API from openAI, passing the prompt described. Notice that we can reference others nodes
outputs directly in the prompt (they are turned to strings when executing this node). 

Also, notice that we are passing several tools for function calling (which are optional). 
You can use [Composio](https://composio.dev) tools with the syntax COMPOSIO.composio_tool_name. 
You can use any tool from [langchain_community.tools](https://python.langchain.com/api_reference/community/tools.html) with the syntax "LANGCHAIN.langchain_tool_name".

Besides function calling, we can also work with [structured outputs](https://platform.openai.com/docs/guides/structured-outputs). Structured outputs is a great 
practical feature that allows you to enforce a predetermined schema from the openAI API call. Using it ensures the model will always generate responses that adhere to your supplied schema. So, if you want the node output to be of the type

``
{'field_1':value_1, 'field_2':value_2}
``

where the values are strings, you first define a pydantic model that defines the schema on a separate schemas.py file


``
from pydantic import BaseModel

class ResponseSchema(BaseModel):,
            field_1: str = Field(..., description="Field 1 description"),
            field_2: str = Field(..., description="Field 2 description")
``

and then pass it in the YAML file as a field in the llm_service node


```yaml
- name: generate_summary
  type: llm_service
  service: openai
  model: "gpt-4"
  structured_output_schema: ResponseSchema
  params:
    prompt: |
      Summarize the following data:
      {{ process_data.processed_data }}
  outputs:
    - summary
```

The output of this node will then be an instance of the class ResponseSchema that we defined. If we want to transform this to a dictionary or do any other
further post-processing, we should create a separate node for that. 

Like when workinf with functions, we don't pass the path of the schemas.py file directly in the YAML file, but will do it when using `GenFlow` to execute
the workflow. 


#### YML Flow Nodes

Used to include and execute another YAML workflow within the current workflow.

**Example:**

```yaml
- name: sub_workflow
  type: yml_flow
  yml_file: sub_workflow.yaml
  params:
    input_data: '{{ generate_summary.summary }}'
  outputs:
    - subflow_output
```

This will trigger the entire execution of the workflow defined on `sub_workflow.yaml`. The path on the `yml_file` field should be relative to where the parente
YAML file is located.

### 1.3 Parameters and Outputs

- **Parameters (`params`)**: Inputs required for the node to execute. You can reference outputs from previous nodes using the syntax `{{ node_name.output_name }}`.
- **Outputs (`outputs`)**: The data produced by the node, which can be used by subsequent nodes.

### 1.4 Referencing Outputs

Use the Jinja2 templating syntax to reference outputs from other nodes:

```yaml
params:
  input_data: '{{ previous_node.output_name }}'
```

---

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

## 3. Integrations

GenSphere supports integration with external tools and platforms to enhance your workflows.

### 3.1 Composio Tools

[Composio](https://composio.dev/) provides a set of tools that can be used within your GenSphere workflows.

#### Using Composio Tools

- Refer to Composio tools in the `tools` field with the syntax `COMPOSIO.tool_name`.
- Ensure you have set your `COMPOSIO_API_KEY` in your environment variables.

**Example YAML Node:**

```yaml
- name: web_scraping
  type: llm_service
  service: openai
  model: "gpt-4"
  tools:
    - COMPOSIO.FIRECRAWL_SCRAPE
  params:
    prompt: |
      Scrape the content from the following URL:
      {{ url_to_scrape }}
  outputs:
    - scraped_content
```

### 3.2 LangChain Tools

[LangChain](https://langchain.com) offers a suite of tools for building applications with language models.

#### Using LangChain Tools

- Refer to LangChain tools in the `tools` field with the syntax `LANGCHAIN.tool_name`.
- Ensure the required LangChain packages are installed.

**Example YAML Node:**

```yaml
- name: data_analysis
  type: llm_service
  service: openai
  model: "gpt-4"
  tools:
    - LANGCHAIN.PandasDataFrameAnalyzer
  params:
    prompt: |
      Analyze the following data:
      {{ data_frame }}
  outputs:
    - analysis_result
```

### 3.3 Custom Tools

You can also use custom functions as tools in **llm_service** nodes.

**Example:**

```yaml
- name: custom_tool_usage
  type: llm_service
  service: openai
  model: "gpt-4"
  tools:
    - my_custom_function
  params:
    prompt: |
      Use the custom function to process the data.
  outputs:
    - custom_tool_output
```

Ensure `my_custom_function` is defined in your functions file.

---

## 4. Lists and Iterables

Working with lists and iterables in GenSphere allows you to process collections of data efficiently.

### 4.1 Processing Lists

When a node produces a list output, you can process each element individually in subsequent nodes.

#### Referencing List Elements

Use the `[i]` syntax to reference individual elements in a list.

**Example:**

```yaml
- name: process_items
  type: function_call
  function: process_item_function
  params:
    item: '{{ item_list.items[i] }}'
  outputs:
    - processed_items
```

### 4.2 Iterating Over Lists

GenSphere automatically detects when you reference a list element and iterates over the list, executing the node for each element.

#### Example Workflow

Suppose you have a list of items you want to process individually.

**Node Producing a List:**

```yaml
- name: get_items
  type: function_call
  function: get_items_function
  outputs:
    - items  # This is a list
```

**Node Processing Each Item:**

```yaml
- name: process_each_item
  type: function_call
  function: process_item_function
  params:
    item: '{{ get_items.items[i] }}'
  outputs:
    - processed_items
```

**Key Points:**

- The node `process_each_item` will be executed for each element in `get_items.items`.
- The outputs will be collected into a list `processed_items`.

### 4.3 Collecting Outputs

After iterating over a list, the outputs are collected into a list corresponding to each input element.

**Accessing Collected Outputs:**

```python
processed_items = flow.outputs['process_each_item']['processed_items']
for item in processed_items:
    print(item)
```

### 4.4 Nested Iterations

You can perform nested iterations by referencing elements within elements.

**Example:**

```yaml
- name: process_nested_items
  type: function_call
  function: process_nested_function
  params:
    sub_item: '{{ get_items.items[i].sub_items[j] }}'
  outputs:
    - nested_processed_items
```

**Note:** Be cautious with nested iterations as they can significantly increase the number of executions.

---

## Next Steps

Now that you've learned about workflows, functions and schemas, integrations, and working with lists, you're ready to explore more advanced features of GenSphere:

- **[Nesting Workflows](nesting_workflows.md)**: Learn how to create modular and reusable workflows.
- **[Visualization](visualization.md)**: Understand how to visualize workflows for better insight.
- **[Execution](execution.md)**: Dive deeper into executing workflows and handling outputs.
- **[Using the Hub](hub.md)**: Discover how to share and access workflows on the GenSphere platform.

---

## Additional Resources

- **[GenSphere GitHub Repository](https://github.com/octopus2023-inc/gensphere)**
- **[GenSphere Documentation](../index.md)**
- **[Composio SDK Guide](https://app.composio.dev/sdk_guide)**
- **[LangChain Tools API Reference](https://python.langchain.com/api_reference/community/tools.html)**

---

## Feedback

We hope this guide helps you get started with GenSphere. If you have any questions or feedback, please reach out on our [GitHub Issues](https://github.com/octopus2023-inc/gensphere/issues) page.

# End of User Guide Sections

---

Feel free to explore the next sections in the user guide for more detailed information on nesting workflows, visualization, execution, and using the GenSphere Hub.