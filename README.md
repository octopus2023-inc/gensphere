# GenSphere

**GenSphere** is an open-source platform where you can push and pull reusable components 
of LLM applications, and build new applications with them in a very simple way.
---

## Why GenSphere?

GenSphere is built to address four primary needs for AI developers:

### 1. Low-level control 

We break any LLM application down to graphs where each node is either a function call, 
an LLM API call or another graph itself. By doing so, you can inspect (and edit) any 
application down to its core components. We want to avoid the cumbersome pile of 
unnecessary abstractions that some modern frameworks bring.

### 2. Portability

Application are defined by a set of **YAML files and associated python functions and schemas**. 
This make it easy to share your application with other developers, and makes it easy
for them to use what you built in more complex workflows.

### 3. Community collaboration

Once you've broken your application down to its core components as described above, you
can push it to our open platform (no registration required). A public ID is generated,
and your project is now publicly accessible to anyone. You can pull any project by
referencing its ID.

You can also check popularity of published projects, as measured by number of pulls they get.

### 4. Composability

 Because you can reference graphs as nodes on parents graphs, GenSphere makes it extremely easy to compose
complex applications from simpler reusable components. You can pull projects from the 
platform and build with them instead of having to work from scratch. 


---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quickstart Guide](#quickstart-guide)
- [Examples](#examples)
- [How to build agentic systems with GenSphere](#How-to-build-agentic-systems-with-GenSphere)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Define workflows with simple YAML files**: Create complex execution graphs using simple YAML files.
- **Nest LLM applications easily**: You can reference other YAML files as nodes in your workflow, and compose complex systems easily.
- **Push and pull projects to our community hub**: Collaborate with others by publishing and pulling projects from the platform (no registration required). Check the popularity of your projects as measured by the number of times they were used by others.
- **Visualize workflows and gain low-level control**: explore your projects easily with interactive graphical visualization. You can quickly see which functions are attached to which nodes and have complete control over your workflows.

---

## Installation

```bash
pip install gensphere
```
---

## Quickstart guide

### 1. Go over our 5-min tutorial notebook
This notebook contains everything you need to know about GenSphere. 

---
## Examples

[coming soon]

---
## How to build agentic systems with GenSphere

[coming soon]

---
## Contributing

We welcome contributions! Please reach out at our Discord server.

---
## License

This project is licensed under the MIT License - see the LICENSE file for details.