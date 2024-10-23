# graph_builder.py

import yaml
import os
import logging
from typing import Optional, Set, Union, List, Dict

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Change to DEBUG for more detailed logs
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)


def parse_yaml(yaml_file: str) -> dict:
    """
    Parses a YAML file and returns its content.

    Args:
        yaml_file (str): Path to the YAML file.

    Returns:
        dict: Parsed YAML data.
    """
    yaml_file = os.path.abspath(yaml_file)
    if not os.path.exists(yaml_file):
        logger.error(f"YAML file '{yaml_file}' does not exist.")
        raise FileNotFoundError(f"YAML file '{yaml_file}' does not exist.")

    with open(yaml_file, 'r') as f:
        try:
            data = yaml.safe_load(f)
            logger.debug(f"Parsed YAML file '{yaml_file}': {data}")
            return data
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file '{yaml_file}': {e}")
            raise


def extract_referenced_nodes(template_str: str) -> Set[str]:
    """
    Extracts all referenced node names from a templated string.

    Args:
        template_str (str): The templated string, e.g., "{{ node.output }}".

    Returns:
        Set[str]: A set of referenced node names.
    """
    import re
    pattern = r"\{\{\s*([\w_][\w_\d]*)\.[^\}]*\}\}"
    matches = re.findall(pattern, template_str)
    logger.debug(f"Extracted referenced nodes from '{template_str}': {matches}")
    return set(matches)


def traverse_node_fields(node_value: Union[str, Dict, List]) -> Set[str]:
    """
    Recursively traverses a node's fields to find all referenced node names.

    Args:
        node_value: The node value to traverse.

    Returns:
        Set[str]: A set of referenced node names found within the node value.
    """
    referenced_nodes = set()
    if isinstance(node_value, str):
        if '{{' in node_value and '}}' in node_value:
            nodes = extract_referenced_nodes(node_value)
            referenced_nodes.update(nodes)
    elif isinstance(node_value, dict):
        for key, value in node_value.items():
            if key not in {'name', 'type', 'outputs'}:
                nodes_in_key = extract_referenced_nodes(str(key))
                referenced_nodes.update(nodes_in_key)
                nodes_in_value = traverse_node_fields(value)
                referenced_nodes.update(nodes_in_value)
    elif isinstance(node_value, list):
        for item in node_value:
            nodes = traverse_node_fields(item)
            referenced_nodes.update(nodes)
    return referenced_nodes


def identify_and_style_entrypoints_outputs(elements: list) -> list:
    """
    Identifies entrypoint and output nodes based on incoming and outgoing edges and styles them accordingly.

    Args:
        elements (list): List of Cytoscape elements (nodes and edges).

    Returns:
        list: Updated list of Cytoscape elements with styled entrypoints and output nodes.
    """
    incoming_edges = {}
    outgoing_edges = {}

    # Initialize counts
    for elem in elements:
        if 'source' in elem['data'] and 'target' in elem['data']:
            source = elem['data']['source']
            target = elem['data']['target']
            outgoing_edges[source] = outgoing_edges.get(source, 0) + 1
            incoming_edges[target] = incoming_edges.get(target, 0) + 1

    # Iterate through nodes to identify entrypoints and outputs
    for elem in elements:
        if 'label' in elem['data']:
            node_id = elem['data']['id']
            node_type = elem['data'].get('type', '')
            # Check for entrypoint
            if incoming_edges.get(node_id, 0) == 0:
                if 'classes' in elem:
                    elem['classes'] += ' entrypoint-node'
                else:
                    elem['classes'] = 'entrypoint-node'
                logger.debug(f"Marked node '{node_id}' as entrypoint.")
            # Check for output
            if outgoing_edges.get(node_id, 0) == 0:
                if 'classes' in elem:
                    elem['classes'] += ' output-node'
                else:
                    elem['classes'] = 'output-node'
                logger.debug(f"Marked node '{node_id}' as output node.")

    return elements


def build_graph_data(yaml_file: str) -> list:
    """
    Builds graph data compatible with Cytoscape from a YAML workflow definition.

    Args:
        yaml_file (str): Path to the YAML file.

    Returns:
        list: List of Cytoscape elements (nodes and edges).
    """
    data = parse_yaml(yaml_file)
    elements = []
    node_ids = set()
    edges = []

    nodes = data.get('nodes', [])
    if not nodes:
        logger.warning(f"No nodes found in YAML file '{yaml_file}'.")
        return elements  # Return empty list if no nodes

    # Build a mapping from node IDs to node types
    node_type_map = {}

    for node in nodes:
        node_name = node.get('name')
        node_type = node.get('type')

        if not node_name:
            logger.error("A node without a 'name' was found.")
            raise ValueError("All nodes must have a 'name' field.")

        node_id = node_name

        if node_id in node_ids:
            logger.error(f"Duplicate node name '{node_id}' detected.")
            raise ValueError(f"Duplicate node name '{node_id}' detected.")

        node_ids.add(node_id)
        node_type_map[node_id] = node_type

        # Prepare node data with default fields to prevent null values
        node_data = {
            'id': node_id,
            'label': node_name,
            'type': node_type,
            'params': node.get('params', {}),
            'outputs': node.get('outputs', [])
        }

        # Include additional fields based on node type
        if node_type == 'function_call':
            node_data['function'] = node.get('function', '')
            node_data['function_call'] = node.get('function_call', '')
        elif node_type == 'llm_service':
            node_data['tools'] = node.get('tools', [])
            node_data['structured_output_schema'] = node.get('structured_output_schema', '')
        elif node_type == 'yml_flow':
            node_data['yml_file'] = node.get('yml_file', '')
        # Add other node types as needed

        # Add node element
        element = {
            'data': node_data,
            'classes': node_type  # Used for styling in Cytoscape
        }
        elements.append(element)
        logger.debug(f"Added node: {element}")

    # After all nodes are added, create edges
    for node in nodes:
        node_name = node.get('name')
        node_id = node_name

        # Handle dependencies by traversing all node fields
        node_fields = node.copy()
        # Exclude certain keys that do not contain dependencies
        excluded_keys = {'name', 'type', 'outputs'}
        for key in excluded_keys:
            node_fields.pop(key, None)
        referenced_nodes = traverse_node_fields(node_fields)
        logger.debug(f"Node '{node_id}' references nodes: {referenced_nodes}")
        for referenced_node in referenced_nodes:
            referenced_node_id = referenced_node
            if referenced_node_id in node_ids:
                edge_classes = 'dependency-edge'  # Default edge class
                # Check if target node is a yml_flow
                target_node_type = node_type_map.get(node_id, '')
                if target_node_type == 'yml_flow':
                    edge_classes += ' edge-to-yml-flow'
                dependency_edge = {
                    'data': {'source': referenced_node_id, 'target': node_id},
                    'classes': edge_classes  # Used for styling dependency edges
                }
                edges.append(dependency_edge)
                logger.debug(f"Added dependency edge from '{referenced_node_id}' to '{node_id}': {dependency_edge}")
            else:
                logger.warning(f"Referenced node '{referenced_node_id}' not found for dependency in node '{node_id}'.")

    # Combine nodes and edges
    elements.extend(edges)

    # Identify and style entrypoints and output nodes
    elements = identify_and_style_entrypoints_outputs(elements)

    # Log the elements for debugging
    logger.info(f"Total elements generated: {len(elements)}")
    logger.debug(f"Elements: {elements}")

    return elements
