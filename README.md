# 🌐 GenSphere
[![Github All Releases](https://img.shields.io/github/downloads/octopus2023-inc/gensphere/total.svg)]()

GenSphere is an open platform to share reusable components of LLM applications and an open-source framework
to combine them into complex workflows. **Think of a mix of HuggingFace and Docker for LLMs.**

---

![gensphere_workflow_example](img/gensphere_workflow_example.png)


## What is GenSphere?

GenSphere is an open platform to share reusable components of LLM-based applications (functions, workflows, schemas) and an SDK for combining those components in an easy way.

### 1. Low-level control 

We break any LLM application down to graphs where each node is either a function call, 
an LLM API call or another graph itself. By doing so, you can inspect (and edit) any 
application down to its core components. **We want to break the cumbersome pile of 
unnecessary abstractions** that some modern frameworks bring, and which have turned LLM application building 
quite opaque.

### 2. Portability

Projects are defined by a set of **YAML files and associated python functions and schemas**. 
This make it easy to share your application with other developers, and makes it easy
for them to use what you built in more complex workflows.

### 3. Community collaboration

Once you've broken your application down to its core components as described above, you
can **push it to an open platform (no registration required)**. A public ID is generated,
and your project is now publicly accessible to anyone. You can pull any project by
referencing its ID.

You can also check popularity of published projects, as measured by number of pulls they get.

### 4. Composability

 Because you can reference graphs as nodes on parents graphs, GenSphere makes it extremely easy to 
 **compose complex applications from simpler reusable components**. You can pull projects from the 
platform and build with them instead of having to work from scratch. 


---

## Table of Contents

- [Features](#features)
- [How does it work?](#how-does-it-work)
- [Notes about this version](#notes-about-this-version)
- [Installation](#installation)
- [Quickstart Guide](#quickstart-guide)
- [Examples](#examples)
- [How to build agentic systems with GenSphere](#How-to-build-agentic-systems-with-GenSphere)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Define workflows with simple YAML files**: Create complex execution graphs using simple YAML files.
- **Gain low-level control**: GenSphere projects break workflows down to individual function calls and/or AI API calls. By doing so, you know exactly what's going on whenever running your application. 
- **Nest LLM applications easily**: You can reference other YAML files as nodes in your workflow, and compose complex systems easily, while maintaining control.
- **Push and pull projects to the open community hub**: Collaborate with others by publishing and pulling projects from the platform (no registration required). 
- **Track popularity of your projects**: Check the popularity of your projects as measured by the number of times they were used by others.
- **Visualize workflows**: explore your projects easily with interactive graphical visualization. You can quickly see which functions are attached to which nodes and have complete control over your workflows.

---


## How does it work?

- **1. Define your workflow with yaml files**: Your project is defined by 3 files:
  
  a) yaml file which represents a graph, where each node is a task to be executed, and which can receive inputs from other nodes. Every node is either a
python function call (see below), an AI API call or another yaml file itself.

  b) a functions.py file, which contains python functions to be executed in the yaml nodes, or to be used as tools for LLMs
  
  c) a schemas.py file which contains pydantic models (that you can use for structured output schema from openAI)   

- **2. Compose complex workflows by nesting graphs**: A node can also be another graph itself, and the SDK will 
take care to resolve dependencies, check consistency and compose a final execution graph. 

- **3. Define your functions and schemas**: Create a .py file with all functions you are planning to use
in your project, be it as individual nodes in the execution graph or as [tools for function calling by LLMs.](https://platform.openai.com/docs/guides/function-calling)
You can also create a separate .py file with pydantic models if you want to use openAI [structured output feature in any given node.](https://platform.openai.com/docs/guides/structured-outputs).
If you are new to pydantic and openAI structured outputs, check this [short tutorial.](https://www.datacamp.com/tutorial/open-ai-structured-outputs)

- **4. Leverage integration with LangChain and Composio**: when doing function calling, you can leverage tools 
available in both [Composio](https://composio.dev/) and [Langchain](https://python.langchain.com/v0.1/docs/modules/tools/). 
Check the implementation notebook for further details. 

- **5. Visualize your project**: GenSphere creates an interactive graphical representation of your project. The SDK 
renders a graph, and you can inspect every node to see which functions or schemas are associated with it, as well
as its parameters and outputs. 

- **6. Execute the workflow**: the GenSphere SDK resolves dependencies and executes your workflow. 

- **7. Push to the platform**: once ready, your project can be pushed to our open platform. You submit you yaml file
and any associated functions or schemas .py files. An ID is generated, and your project becomes publicly accessible.

- **8. Pull from the platform**: you can pull yaml files, functions and schemas from the platform by providing its ID
(generated by the creator of the project in the step above). Its then easy to use these components to build more 
complex LLM applications.

- **9. Watch your projects grow**: you can check popularity of your projects by measuring the number of pulls it received. 

---


## Notes about this version

- In this alpha version, only openAI is supported for AI API calls. We are planning to 
integrate with other major providers.

- Graphs in yaml files need to be [DAGs](https://en.wikipedia.org/wiki/Directed_acyclic_graph). We are
planning to allow for cycles, which will unlock full agentic system building using only GenSphere.

- Feedback is welcome! Please [reach out by email](mailto:octopus2023.contact@gmail.com) or join our 
[discord server](https://discord.gg/DZFWMXJv).
 
---


## Installation

```bash
pip install gensphere
```
---

## Quickstart guide

Import necessary modules

```
from gensphere.genflow import GenFlow
from gensphere.hub import Hub
from dotenv import load_dotenv
```
Load your enviroment variables, with OPENAI_API_KEY defined there.

```
load_dotenv()
```

Pull a project from the platform

```
hub=Hub()
hub.pull(push_id='2c03079c-0e33-489e-bbbe-777da744d56f',
         yaml_filename='simple_examples.yaml',
         functions_filename='simple_examples_functions.py',
         save_to_disk=True)
```

This saves simple_examples.yaml and simple_examples_functions.py to your current working diretory. Now you can execute the flow with. 

```
flow=GenFlow('simple_examples.yaml','simple_examples_functions.py')
flow.parse_yaml()
flow.run()
```

You can access nodes outputs with

```
flow.outputs
```

### Go over our 5-min tutorial notebook
This [notebook](https://github.com/octopus2023-inc/gensphere/blob/main/gensphere_tutorial.ipynb) contains everything you need to know about GenSphere, including yaml syntax, visualizastion, yaml parsing, nesting workflows, etc. 

---
## Examples

[coming soon]

---
## How to build agentic systems with GenSphere

[coming soon]

---
## Contributing

We welcome contributions! Please [reach out by email](mailto:octopus2023.contact@gmail.com) and join our [Discord server](https://discord.gg/DZFWMXJv).

---
## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=octopus2023-inc/gensphere&type=Date)](https://star-history.com/#octopus2023-inc/gensphere&Date)
