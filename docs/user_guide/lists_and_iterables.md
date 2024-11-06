## 5. Lists and Iterables

Working with lists and iterables in GenSphere allows you to process collections of data efficiently.

### 5.1 Processing Lists

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

### 5.2 Iterating Over Lists

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

### 5.3 Collecting Outputs

After iterating over a list, the outputs are collected into a list corresponding to each input element.

**Accessing Collected Outputs:**

```python
processed_items = flow.outputs['process_each_item']['processed_items']
for item in processed_items:
    print(item)
```

---
