## 6. Visualization

Visualizing your workflow helps you understand the execution flow and dependencies between nodes. GenSphere provides a visualization tool to render your workflow as an interactive graph.

### 6.1 Using the Visualizer

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
### 6.2 Features of the Visualizer

- **Interactive Graph**: Nodes are displayed as a graph where you can zoom in/out.
- **Node Details**: Click on a node to see details such as inputs, outputs, functions, and schemas.
- **Execution Flow**: Visualize the dependencies and execution order.

### 6.3 Running the Visualizer

When you run `viz.start_visualization()`, the visualizer starts a local web server. Open your browser and navigate to `http://127.0.0.1:8050` (or the specified address and port) to view the visualization.

**Note:** If you're running in an environment like Google Colab, you might need to set up port forwarding or use a different method to access the visualization.

---
