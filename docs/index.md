# 🌐 GenSphere Documentation

Welcome to the official documentation for **GenSphere**, a declarative framework to build LLM applications and an open platform to push and pull them. Think of GenSphere as **Docker for LLM applications**.

---

## Introduction

### What is GenSphere?

GenSphere is a framework that allows you to build Large Language Model (LLM) applications by declaring tasks and how they connect using YAML files. It breaks down any LLM application into graphs where each node is either a function call, an LLM API call, or another graph itself. This approach provides:

- **Low-Level Control**: Inspect and edit applications down to their core components, avoiding unnecessary abstractions.
- **Portability**: Projects are defined by YAML files and associated Python functions and schemas, making sharing easy.
- **Community Collaboration**: Push your application to an open platform (no registration required) and generate a public ID to make it accessible to anyone.
- **Composability**: Easily compose complex applications from simpler, reusable components.

### Key Features

- **Define Workflows with Simple YAML Files**: Create complex execution graphs using simple YAML files.
- **Gain Low-Level Control**: Break workflows down to individual function calls and/or AI API calls.
- **Nest LLM Applications Easily**: Reference other YAML files as nodes in your workflow.
- **Push and Pull Projects to the Open Community Hub**: Collaborate by publishing and pulling projects from the platform.
- **Track Popularity of Your Projects**: Check how popular your projects are by the number of times they are used by others.
- **Visualize Workflows**: Explore your projects with interactive graphical visualization.

### Why Use GenSphere?

GenSphere provides a transparent and flexible way to build LLM applications without the cumbersome abstractions that some modern frameworks introduce. It promotes collaboration and reuse by enabling developers to share and compose workflows easily.

### How Does GenSphere Work?

1. **Define Your Workflow with YAML Files**: Your project is defined by YAML files representing graphs where each node is a task to be executed.
2. **Compose Complex Workflows by Nesting Graphs**: Reference other YAML files as nodes to build upon existing workflows.
3. **Define Your Functions and Schemas**: Create Python files with functions and Pydantic models for structured outputs.
4. **Leverage Integration with LangChain and Composio**: Utilize tools available in [Composio](https://composio.dev/) and [LangChain](https://python.langchain.com/).
5. **Visualize Your Project**: Generate interactive graphical representations of your workflows.
6. **Execute the Workflow**: GenSphere resolves dependencies and executes your workflow.
7. **Push to the Platform**: Share your project on the open platform with a generated ID.
8. **Pull from the Platform**: Use projects from others to build more complex applications.
9. **Watch Your Projects Grow**: Monitor the popularity of your projects by tracking the number of pulls.

---

## Getting Started

- **[Installation](getting_started/installation.md)**
- **[Quickstart Guide](getting_started/quickstart.md)**

## Tutorials

- **[Quickstart Tutorial](tutorials/tutorial.md)**

## User Guide

- **[Workflows](user_guide/workflows.md)**
- **[Functions and schemas](user_guide/functions_and_schemas.md)**
- **[Nesting workflows](user_guide/nesting_workflows.md)**
- **[Integration with Composio and Langchain](user_guide/integration_with_composion_and_langchain.md)**
- **[Visualization](user_guide/visualization.md)**
- **[Execution](user_guide/execution.md)**

## API reference

- **[API reference](api_reference/api_reference.md)**

## Contributing

We welcome contributions! Please join our [Discord server](https://discord.gg/DZFWMXJv).

---

![Star History Chart](https://api.star-history.com/svg?repos=octopus2023-inc/gensphere&type=Date)

