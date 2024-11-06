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
