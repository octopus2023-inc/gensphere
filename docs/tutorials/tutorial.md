# GenSphere Tutorial

Welcome to the **GenSphere** tutorial! In this guide, we'll walk you through the main functionalities of GenSphere, an AI agent development framework that simplifies the creation and execution of complex workflows involving functions and language models.

By completing this tutorial, you will learn how to:

1. Define workflows using YAML files.
2. Use pre-built components from the GenSphere platform.
3. Nest workflows to create complex pipelines.
4. Utilize custom functions and schemas, and integrate with LangChain and Composio tools.
5. Visualize workflows for better understanding.
6. Push and pull workflows to and from the GenSphere platform.

You can also run this example directly on [Google Colab here](https://github.com/octopus2023-inc/gensphere/blob/main/examples/gensphere_tutorial.ipynb). Let's get started!

---

## Table of Contents

1. [Installation](#1-installation)
2. [Importing GenSphere](#2-importing-gensphere)
3. [Setting Up Environment Variables](#3-setting-up-environment-variables)
4. [Defining Your Workflow with YAML](#4-defining-your-workflow-with-yaml)
   - [4.1 Pulling a Base YAML File](#41-pulling-a-base-yaml-file)
   - [4.2 Visualizing Your Project](#42-visualizing-your-project)
   - [4.3 Understanding the YAML Syntax](#43-understanding-the-yaml-syntax)
     - [Function Call Nodes](#function-call-nodes)
     - [LLM Service Nodes](#llm-service-nodes)
     - [YML Flow Nodes](#yml-flow-nodes)
     - [Working with Lists](#working-with-lists)
5. [Combining Workflows](#5-combining-workflows)
6. [Running Your Project](#6-running-your-project)
7. [Pushing to the Platform](#7-pushing-to-the-platform)
8. [Checking Project Popularity](#8-checking-project-popularity)
9. [Conclusion](#9-conclusion)

---

## 1. Installation

First, ensure you have **Python 3.10** or higher installed on your system. Then, install GenSphere and other required libraries using `pip`:

```bash
pip install gensphere
```

---

## 2. Importing GenSphere

In your Python script or Jupyter notebook, import the necessary modules:

```python
import logging
import os
from gensphere.genflow import GenFlow
from gensphere.yaml_utils import YamlCompose
from gensphere.visualizer import Visualizer
from gensphere.hub import Hub
```

Set up logging to monitor the execution:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode='w'),
        logging.StreamHandler()
    ]
)
```

---

## 3. Setting Up Environment Variables

If you haven't defined your enviroment variables yet, you can do so now. Replace the placeholders with your actual API keys. You'll need API keys for **OpenAI**, **Composio**, and **FireCrawl**.

```python
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY'
os.environ['COMPOSIO_API_KEY'] = 'YOUR_COMPOSIO_API_KEY'  # Visit composio.dev to get one
os.environ['FIRECRAWL_API_KEY'] = 'YOUR_FIRECRAWL_API_KEY'  # Visit firecrawl.dev to get one
```

---

## 4. Defining Your Workflow with YAML

Our goal is to create a workflow that automatically finds the latest product releases on [Product Hunt](https://www.producthunt.com), explores their revenue and traction, and analyzes a new startup idea based on that information.

### 4.1 Pulling a Base YAML File

We will use a **pre-built workflow** from the GenSphere open platform that extracts information from Product Hunt. This workflow will be nested into a larger workflow to achieve our objective.

#### Pulling from the Platform

Use the `Hub` class to pull the base YAML file, along with its associated functions and schema files:

```python
# Define paths to save the files
path_to_save_yaml_file = 'product_hunt_analyzer.yaml'
path_to_save_functions_file = 'gensphere_functions.py'
path_to_save_schema_file = 'structured_output_schema.py'

# Initialize the Hub
hub = Hub()

# Pull the files using the push_id
hub.pull(
    push_id='de8afbeb-06cb-4f8f-8ead-64d9e6ef5326',
    yaml_filename=path_to_save_yaml_file,
    functions_filename=path_to_save_functions_file,
    schema_filename=path_to_save_schema_file,
    save_to_disk=True
)
```

#### Examining the YAML File

The YAML file `product_hunt_analyzer.yaml` has been saved locally. Here's the content:

```yaml
# product_hunt_analyzer.yaml

nodes:
  - name: get_current_date
    type: function_call
    function: get_current_date_function
    outputs:
      - current_date

  - name: get_timewindow
    type: function_call
    function: get_timewindow_function
    outputs:
      - time_window

  - name: product_hunt_scrape
    type: llm_service
    service: openai
    model: "gpt-4o-2024-08-06"
    tools:
      - COMPOSIO.FIRECRAWL_SCRAPE
    params:
      prompt: |
        You should visit Product Hunt at https://www.producthunt.com/leaderboard/monthly/yyyy/mm
        Today is {{ get_current_date.current_date }}
        Substitute yyyy and mm with the year and month you want to search.
        The search time window should be {{ get_timewindow.time_window }}.
        Extract raw content from the HTML pages, which contain information about new product launches, companies, number of upvotes, etc.
        Scroll the page until the end and wait a few milliseconds before scraping.

    outputs:
      - product_hunt_scrape_results

  - name: extract_info_from_search
    type: llm_service
    service: openai
    model: "gpt-4o-2024-08-06"
    structured_output_schema: StartupInformationList
    params:
      prompt: |
        You are given reports from a search on Product Hunt containing products featured last month:
        {{ product_hunt_scrape.product_hunt_scrape_results }}.
        Extract accurate information about these new product launches.
        Structure the information with the following dimensions: product name, company name, company URL, number of upvotes, business model, and brief description.

    outputs:
      - structured_search_info

  - name: postprocess_search_results
    type: function_call
    function: postprocess_search_results_function
    params:
      info: '{{ extract_info_from_search.structured_search_info }}'
    outputs:
      - postprocessed_search_results

  - name: find_extra_info
    type: llm_service
    service: openai
    model: "gpt-4o-2024-08-06"
    tools:
      - COMPOSIO.TAVILY_TAVILY_SEARCH
    params:
      prompt: |
        Conduct a comprehensive web search about the following entry from Product Hunt:
        {{ postprocess_search_results.postprocessed_search_results[i] }}.
        Find relevant news about the company, especially related to revenue, valuation, traction, acquisition, number of users, etc.

    outputs:
      - startup_extra_info
```

### 4.2 Visualizing Your Project

To better understand the workflow, use the `Visualizer` class to visualize the project:

```python
viz = Visualizer(
    yaml_file='product_hunt_analyzer.yaml',
    functions_file='gensphere_functions.py',
    schema_file='structured_output_schema.py',
    address='127.0.0.1',
    port=8050
)
viz.start_visualization()
```

**Note:** Running the visualization inside environments like Google Colab might be cumbersome. It's recommended to run it locally and access it through your browser.

### 4.3 Understanding the YAML Syntax

GenSphere uses a YAML-based syntax to define workflows. There are three types of nodes:

1. **Function Call Nodes** (`function_call`)
2. **LLM Service Nodes** (`llm_service`)
3. **YML Flow Nodes** (`yml_flow`)

#### Function Call Nodes

These nodes trigger the execution of Python functions defined in a separate `.py` file. They have `params` and `outputs` fields.

**Example:**

```yaml
- name: get_current_date
  type: function_call
  function: get_current_date_function
  outputs:
    - current_date
```

**Function Definition (`gensphere_functions.py`):**

```python
# gensphere_functions.py

from datetime import datetime

def get_current_date_function():
    """
    Returns the current date as a string.

    Returns:
        dict: A dictionary with 'current_date' as key and current date as value.
    """
    return {'current_date': datetime.today().strftime('%Y-%m-%d')}
```

**Key Points:**

- **Function Outputs**: The function must return a dictionary whose keys match the `outputs` defined in the YAML file.
- **Referencing Outputs**: Use the syntax `{{ node_name.output_name }}` to reference outputs from other nodes in the `params` field.

#### LLM Service Nodes

These nodes execute calls to language model APIs. Currently, GenSphere supports OpenAI's API, including **structured outputs** and **function calling**.

**Example:**

```yaml
- name: product_hunt_scrape
  type: llm_service
  service: openai
  model: "gpt-4o-2024-08-06"
  tools:
    - COMPOSIO.FIRECRAWL_SCRAPE
  params:
    prompt: |
      You should visit Product Hunt at https://www.producthunt.com/leaderboard/monthly/yyyy/mm
      Today is {{ get_current_date.current_date }}
      Substitute yyyy and mm with the year and month you want to search.
      The search time window should be {{ get_timewindow.time_window }}.
      Extract raw content from the HTML pages, which contain information about new product launches, companies, number of upvotes, etc.
      Scroll the page until the end and wait a few milliseconds before scraping.

  outputs:
    - product_hunt_scrape_results
```

**Key Points:**

- **Tools Field**: Can refer to functions in your `.py` file, Composio tools (`COMPOSIO.tool_name`), or LangChain tools (`LANGCHAIN.tool_name`).
- **Structured Outputs**: Use the `structured_output_schema` field to specify a Pydantic schema for the expected output.

**Structured Output Example:**

```yaml
- name: extract_info_from_search
  type: llm_service
  service: openai
  model: "gpt-4o-2024-08-06"
  structured_output_schema: StartupInformationList
  params:
    prompt: |
      You are given reports from a search on Product Hunt containing products featured last month:
      {{ product_hunt_scrape.product_hunt_scrape_results }}.
      Extract accurate information about these new product launches.
      Structure the information with the following dimensions: product name, company name, company URL, number of upvotes, business model, and brief description.

  outputs:
    - structured_search_info
```

**Schema Definition (`structured_output_schema.py`):**

```python
# structured_output_schema.py

from pydantic import BaseModel, Field
from typing import List

class StartupInformation(BaseModel):
    product_name: str = Field(..., description="The name of the product")
    company_name: str = Field(..., description="The name of the company offering the product")
    url: str = Field(..., description="URL associated with the product")
    number_upvotes: int = Field(..., description="Number of upvotes the product has received")
    business_model: str = Field(..., description="Brief description of the business model")
    brief_description: str = Field(..., description="Brief description of the product")

class StartupInformationList(BaseModel):
    information_list: List[StartupInformation]
```

**Post-Processing Node:**

After obtaining structured output, we want post-process it. The output is an instance of the class `StartupInformationList`, which is a list of `StartupInformation` instances, as defined in the pydantic mode. We want to extract this as a list, so we applu the `postprocess_search_results_function`.

```yaml
- name: postprocess_search_results
  type: function_call
  function: postprocess_search_results_function
  params:
    info: '{{ extract_info_from_search.structured_search_info }}'
  outputs:
    - postprocessed_search_results
```

**Function Definition (`gensphere_functions.py`):**

```python
def postprocess_search_results_function(info):
    """
    Processes the structured search information.

    Args:
        info (StartupInformationList): The structured search info.

    Returns:
        dict: A dictionary with 'postprocessed_search_results' as key.
    """
    result = info.model_dump().get('information_list')
    return {'postprocessed_search_results': result}
```

#### YML Flow Nodes

These nodes represent entire YAML files themselves, allowing you to nest workflows.

**Example:**

```yaml
- name: product_hunt_analyzer
  type: yml_flow
  yml_file: product_hunt_analyzer.yaml
  outputs:
    - postprocessed_search_results
    - startup_extra_info
```

**Key Points:**

- **Nested Workflows**: GenSphere will handle dependencies and compose a combined YAML file that is ready to run.
- **Parameters**: You can pass parameters to the nested workflow using the `params` field.

#### Working with Lists

When the output of a node is a list, you might want to apply the next node to each element individually.

**Syntax:**

- Use `{{ node_name.output_name[i] }}` in the `params` or `prompt` field.
- GenSphere will execute the node for each element and collect the outputs as a list.

**Example:**

```yaml
- name: find_extra_info
  type: llm_service
  service: openai
  model: "gpt-4o-2024-08-06"
  tools:
    - COMPOSIO.TAVILY_TAVILY_SEARCH
  params:
    prompt: |
      Conduct a comprehensive web search about the following entry from Product Hunt:
      {{ postprocess_search_results.postprocessed_search_results[i] }}.
      Find relevant news about the company, especially related to revenue, valuation, traction, acquisition, number of users, etc.

  outputs:
    - startup_extra_info
```

**Key Points:**

- **Iterative Processing**: The node will process each item in `postprocessed_search_results` individually.
- **Collected Outputs**: Outputs are collected into a list corresponding to each input item.

---

## 5. Combining Workflows

Now, we'll embed the `product_hunt_analyzer` workflow into a larger workflow to analyze a new startup idea.

### Defining the New Workflow

Create a new YAML file named `startup_idea_evaluator.yaml`:

```yaml
# startup_idea_evaluator.yaml

nodes:
  - name: read_idea
    type: function_call
    function: read_file_as_string
    params:
      file_path: "domains_to_search.txt"
    outputs:
      - domains

  - name: product_hunt_analyzer
    type: yml_flow
    yml_file: product_hunt_analyzer.yaml
    outputs:
      - postprocessed_search_results
      - startup_extra_info

  - name: generate_report
    type: llm_service
    service: openai
    model: "gpt-4o-2024-08-06"
    params:
      prompt: |
        You are a world-class VC analyst. You are analyzing the following startup idea:
        {{ read_idea.domains }}
        Your task is to analyze this idea in the context of recent launches on Product Hunt.
        Recent launches are:
        {{ product_hunt_analyzer.postprocessed_search_results }}
        Additional information about these companies:
        {{ product_hunt_analyzer.startup_extra_info }}.

        Create a detailed report containing:
        1. An overview of recent launches on Product Hunt. What are the main ideas being explored?
        2. A list of companies from Product Hunt that may become direct competitors to the startup idea. Explain your rationale.
        3. A list of the most promising startups from the Product Hunt launches, based on valuation, revenue, traction, or other relevant metrics.
        4. A table containing all information found from the Product Hunt launches.

        Answer in markdown format.

    outputs:
      - report
```

### Composing the Combined Workflow

Use `YamlCompose` to create a combined YAML file that resolves all dependencies:

```python
# Assuming 'startup_idea_evaluator.yaml' is in the current directory
composer = YamlCompose(
    yaml_file='startup_idea_evaluator.yaml',
    functions_filepath='gensphere_functions.py',
    structured_output_schema_filepath='structured_output_schema.py'
)
combined_yaml_data = composer.compose(save_combined_yaml=True, output_file='combined.yaml')
```

**Note:** Ensure all referenced functions and schemas are available in the specified files.

### Visualizing the Combined Workflow

You can visualize the combined workflow to verify that nesting has been handled correctly:

```python
viz = Visualizer(
    yaml_file='combined.yaml',
    functions_file='gensphere_functions.py',
    schema_file='structured_output_schema.py',
    address='127.0.0.1',
    port=8050
)
viz.start_visualization()
```

---

## 6. Running Your Project

Now that you have the combined YAML file and necessary Python files, you can execute the workflow.

### Preparing Input Files

The first node `read_idea` expects a text file named `domains_to_search.txt`. Create this file with your startup idea:

```python
startup_idea = """
A startup that creates interactive voice agents using generative AI with emphasis on applications like
language tutoring, entertainment, or mental health. The business model would be B2C.
"""

with open("domains_to_search.txt", "w") as text_file:
    text_file.write(startup_idea)
```

### Executing the Workflow

Initialize `GenFlow` and run the workflow:

```python
flow = GenFlow(
    yaml_file='combined.yaml',
    functions_filepath='gensphere_functions.py',
    structured_output_schema_filepath='structured_output_schema.py'
)
flow.parse_yaml()
flow.run()
```

### Accessing the Outputs

After execution, you can access the results:

```python
# Access all outputs
outputs = flow.outputs

# Print the final report
final_report = outputs.get("generate_report").get("report")

# Display the report in Markdown format
from IPython.display import display, Markdown
display(Markdown(final_report))
```

---

## 7. Pushing to the Platform

You can push your project to the GenSphere platform, allowing others to pull and use it.

```python
hub = Hub(
    yaml_file='combined.yaml',
    functions_file='gensphere_functions.py',
    schema_file='structured_output_schema.py'
)

result = hub.push(push_name='Workflow to analyze startup idea based on recent Product Hunt launches.')
```

Retrieve and print the `push_id`:

```python
print(f"Push ID: {result.get('push_id')}")
print(f"Uploaded Files: {result.get('uploaded_files')}")
```

---

## 8. Checking Project Popularity

Check how many times your project has been pulled from the platform:

```python
# Replace with your actual push_id
push_id = result.get('push_id')

# Get the total number of pulls for the push_id
total_pulls = hub.count_pulls(push_id=push_id)
print(f"Total pulls for push_id {push_id}: {total_pulls}")
```

---

## 9. Conclusion

Congratulations! You've successfully:

- Defined workflows using YAML files.
- Used pre-built components and nested workflows.
- Integrated custom functions, schemas, and external tools.
- Visualized your workflow for better understanding.
- Executed the workflow and accessed the outputs.
- Pushed your project to the GenSphere platform.

---

## Additional Resources

- **GenSphere GitHub Repository**: [https://github.com/octopus2023-inc/gensphere](https://github.com/octopus2023-inc/gensphere)
- **Composio Documentation**: [https://app.composio.dev/sdk_guide](https://app.composio.dev/sdk_guide)
- **LangChain Tools**: [https://python.langchain.com/api_reference/community/tools.html](https://python.langchain.com/api_reference/community/tools.html)

---

## Troubleshooting

If you encounter any issues:

- **API Keys**: Ensure all API keys are correctly set as environment variables.
- **Dependencies**: Verify that all required packages are installed.
- **File Paths**: Double-check the file paths provided to functions and classes.
- **Logs**: Check the `app.log` file for detailed error messages.

---

## Feedback

Your feedback is valuable. If you have suggestions or find any issues, please open an issue on the [GenSphere GitHub repository](https://github.com/octopus2023-inc/gensphere/issues).