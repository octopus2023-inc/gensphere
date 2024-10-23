#yaml_utils.py

import yaml
import os
import logging
import re
from composio_openai import ComposioToolSet, App, Action
import importlib
import networkx as nx
from typing import Union, Set,Tuple, Dict, List
from gensphere.utils import load_module_from_path

# Module-level logger
logger = logging.getLogger(__name__)

def load_module_from_path(file_path):
    import importlib.util
    import sys
    import os

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Cannot find spec for module '{module_name}' at '{file_path}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class YamlCompose:
    """
    Class to compose YAML files by resolving references to other YAML files.
    """

    def __init__(self, yaml_file, functions_filepath,structured_output_schema_filepath):
        self.yaml_file = os.path.abspath(yaml_file)  # Convert to absolute path
        self.functions_filepath = functions_filepath
        self.structured_output_schema_filepath = structured_output_schema_filepath
        self.combined_data = {'nodes': []}
        self.node_name_set = set()  # To keep track of all node names to avoid duplicates.
        # Check if functions_filepath is a valid .py file
        if self.functions_filepath:
            if not os.path.isfile(self.functions_filepath):
                logger.error(f"functions_filepath '{self.functions_filepath}' does not exist.")
                raise FileNotFoundError(f"functions_filepath '{self.functions_filepath}' does not exist.")
            if os.path.splitext(self.functions_filepath)[1] != '.py':
                logger.error("functions_filepath must be a .py file.")
                raise ValueError("functions_filepath must be a .py file.")

        # Check if structured_output_schema_filepath is a valid .py file
        if self.structured_output_schema_filepath:
            if not os.path.isfile(self.structured_output_schema_filepath):
                logger.error(
                    f"structured_output_schema_filepath '{self.structured_output_schema_filepath}' does not exist.")
                raise FileNotFoundError(
                    f"structured_output_schema_filepath '{self.structured_output_schema_filepath}' does not exist.")
            if os.path.splitext(self.structured_output_schema_filepath)[1] != '.py':
                logger.error("structured_output_schema_filepath must be a .py file.")
                raise ValueError("structured_output_schema_filepath must be a .py file.")

    def compose(self, save_combined_yaml=False, output_file='combined.yaml'):
        """
        Starts the composition process and returns the combined YAML data.

        Args:
            save_combined_yaml (bool): If True, saves the combined YAML data to a file.
            output_file (str): The filename to save the combined YAML data.
        """
        logger.info(f"Starting composition with root YAML file '{self.yaml_file}'")
        self._process_yaml_file(self.yaml_file)
        logger.info("Composition completed")

        if save_combined_yaml:
            with open(output_file, 'w') as f:
                yaml.dump(self.combined_data, f)
            logger.info(f"Combined YAML saved to '{output_file}'")

        return self.combined_data

    def _process_yaml_file(self, yaml_file, parent_prefix=''):
        """
        Recursively processes a YAML file, resolving any sub-flow references.

        Args:
            yaml_file (str): Path to the YAML file.
            parent_prefix (str): Prefix to be added to node names for uniqueness.
        """
        yaml_file = os.path.abspath(yaml_file)  # Convert to absolute path
        logger.info(f"Checking for YAML file '{self.yaml_file}' consistency")
        validated, error_msgs, node_outputs = validate_yaml(self.yaml_file,
                                                            self.functions_filepath,
                                                            self.structured_output_schema_filepath)
        if validated:
            logger.info(f"yaml file {self.yaml_file} passed all consistency checks")
        else:
            raise Exception(f"yaml file {self.yaml_file} didn't pass consistency checks.\nError messages: {error_msgs}")

        logger.debug(f"Processing YAML file '{yaml_file}' with prefix '{parent_prefix}'")
        if not os.path.exists(yaml_file):
            logger.error(f"YAML file '{yaml_file}' does not exist.")
            raise FileNotFoundError(f"YAML file '{yaml_file}' does not exist.")

        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        if 'nodes' not in data:
            logger.error(f"YAML file '{yaml_file}' must contain 'nodes'.")
            raise ValueError(f"YAML file '{yaml_file}' must contain 'nodes'.")

        nodes = data['nodes']
        i = 0
        while i < len(nodes):
            node_data = nodes[i]
            node_type = node_data.get('type')
            node_name = node_data.get('name')
            if not node_name:
                logger.error("A node without a 'name' was found.")
                raise ValueError("A node without a 'name' was found.")

            # Create a unique node name by prefixing
            unique_node_name = parent_prefix + node_name
            logger.debug(f"Processing node '{node_name}' (unique name: '{unique_node_name}') of type '{node_type}'")
            if unique_node_name in self.node_name_set:
                logger.error(f"Duplicate node name '{unique_node_name}' detected.")
                raise ValueError(f"Duplicate node name '{unique_node_name}' detected.")

            self.node_name_set.add(unique_node_name)

            if node_type == 'yml_flow':
                # Handle sub-flow
                sub_flow_file = node_data.get('yml_file')
                if not sub_flow_file:
                    logger.error(f"Node '{unique_node_name}' of type 'yml_flow' must have a 'yml_file' field.")
                    raise ValueError(f"Node '{unique_node_name}' of type 'yml_flow' must have a 'yml_file' field.")

                # Compute the absolute path of the sub-flow file
                sub_flow_file_path = os.path.abspath(os.path.join(os.path.dirname(yaml_file), sub_flow_file))
                logger.debug(f"Sub-flow file for node '{unique_node_name}' is '{sub_flow_file_path}'")

                # Get parameters and outputs
                sub_flow_params = node_data.get('params', {})
                sub_flow_outputs = node_data.get('outputs', [])

                # Remove the yml_flow node from the list
                nodes.pop(i)

                # Process sub-flow
                sub_flow_nodes = self._load_yaml_file(sub_flow_file_path)
                # Adjust sub-flow nodes
                adjusted_sub_flow_nodes = self._adjust_sub_flow_nodes(
                    sub_flow_nodes, unique_node_name + '__', sub_flow_params)

                # Add adjusted sub-flow nodes to combined data
                self.combined_data['nodes'].extend(adjusted_sub_flow_nodes)

                # Build output mapping for outputs specified in yml_flow node
                output_mapping = {}
                for output in sub_flow_outputs:
                    # Find the node in sub-flow that produces this output
                    found = False
                    for node in adjusted_sub_flow_nodes:
                        if output in node.get('outputs', []):
                            output_mapping[unique_node_name + '.' + output] = node['name'] + '.' + output
                            found = True
                            break
                    if not found:
                        logger.error(f"Output '{output}' specified in 'yml_flow' node '{unique_node_name}' not produced in sub-flow.")
                        raise ValueError(f"Output '{output}' specified in 'yml_flow' node '{unique_node_name}' not produced in sub-flow.")

                # Adjust references in remaining nodes
                self._adjust_references_in_nodes(nodes[i:], node_name, output_mapping)

                # Do not increment i, as we removed the current node
                continue
            else:
                # Copy node data and adjust the name
                node_data = node_data.copy()
                node_data['name'] = unique_node_name

                # Adjust parameter references to account for prefixed node names
                node_data['params'] = self._adjust_params(node_data.get('params', {}), parent_prefix, set())
                logger.debug(f"Adjusted parameters for node '{unique_node_name}': {node_data['params']}")

                # Add the node to the combined data
                self.combined_data['nodes'].append(node_data)
                logger.debug(f"Added node '{unique_node_name}' to combined data")

                i +=1  # Move to the next node

    def _load_yaml_file(self, yaml_file):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        if 'nodes' not in data:
            logger.error(f"YAML file '{yaml_file}' must contain 'nodes'.")
            raise ValueError(f"YAML file '{yaml_file}' must contain 'nodes'.")
        return data['nodes']

    def _adjust_sub_flow_nodes(self, nodes, sub_flow_prefix, sub_flow_params):
        adjusted_nodes = []
        sub_flow_node_names = set()
        for node_data in nodes:
            node_type = node_data.get('type')
            node_name = node_data.get('name')
            if not node_name:
                logger.error("A node without a 'name' was found in sub-flow.")
                raise ValueError("A node without a 'name' was found in sub-flow.")

            sub_flow_node_names.add(node_name)  # Collect node names in sub-flow

            prefixed_node_name = sub_flow_prefix + node_name
            if prefixed_node_name in self.node_name_set:
                logger.error(f"Duplicate node name '{prefixed_node_name}' detected in sub-flow.")
                raise ValueError(f"Duplicate node name '{prefixed_node_name}' detected in sub-flow.")

            self.node_name_set.add(prefixed_node_name)

            node_data = node_data.copy()
            node_data['name'] = prefixed_node_name

            # Replace parameter references in node params with actual sub_flow_params
            node_data['params'] = self._replace_params(node_data.get('params', {}), sub_flow_params)

            # Adjust any dependencies (in params) to include the sub_flow_prefix
            node_data['params'] = self._adjust_params(node_data.get('params', {}), sub_flow_prefix, sub_flow_node_names)

            adjusted_nodes.append(node_data)

        return adjusted_nodes

    def _replace_params(self, params, sub_flow_params):
        """
        Replaces parameter placeholders in params with the values passed in from the parent flow.

        Args:
            params (dict): The parameters to adjust.
            sub_flow_params (dict): Parameters passed from the parent flow to the sub-flow.

        Returns:
            dict: The adjusted parameters.
        """
        adjusted_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                for param_name, param_value in sub_flow_params.items():
                    pattern = r"\{\{\s*" + re.escape(param_name) + r"\s*\}\}"
                    value = re.sub(pattern, str(param_value), value)
                adjusted_params[key] = value
            else:
                adjusted_params[key] = value
        return adjusted_params

    def _adjust_params(self, params, prefix, sub_flow_node_names):
        """
        Adjusts parameter references to use prefixed node names.

        Args:
            params (dict): The parameters to adjust.
            prefix (str): The prefix for node names.
            sub_flow_node_names (set): Set of node names within the sub-flow.

        Returns:
            dict: The adjusted parameters.
        """
        adjusted_params = {}
        pattern = r"(\{\{\s*)([\w_\.]+)(\s*\}\})"

        for key, value in params.items():
            if isinstance(value, str):
                def replace_func(match):
                    full_match = match.group(0)
                    prefix_match = match.group(1)
                    reference = match.group(2)
                    suffix_match = match.group(3)

                    # Split the reference into parts
                    parts = reference.split('.')
                    first_part = parts[0]
                    rest_parts = parts[1:]

                    # Only adjust if the first part is in sub_flow_node_names
                    if first_part in sub_flow_node_names:
                        adjusted_first_part = prefix + first_part
                    else:
                        adjusted_first_part = first_part

                    adjusted_reference = '.'.join([adjusted_first_part] + rest_parts)

                    return prefix_match + adjusted_reference + suffix_match

                adjusted_value = re.sub(pattern, replace_func, value)
                adjusted_params[key] = adjusted_value
            else:
                adjusted_params[key] = value
        return adjusted_params

    def _adjust_references_in_nodes(self, nodes, yml_flow_node_name, output_mapping):
        """
        Adjusts references in the nodes to replace references to outputs from the yml_flow node.

        Args:
            nodes (list): The list of nodes to adjust.
            yml_flow_node_name (str): The name of the yml_flow node.
            output_mapping (dict): Mapping from yml_flow outputs to sub-flow node outputs.
        """
        for node_data in nodes:
            params = node_data.get('params', {})
            adjusted_params = {}
            for key, value in params.items():
                if isinstance(value, str):
                    for yml_flow_output, sub_flow_output in output_mapping.items():
                        # Replace references like {{ yml_flow_node_name.output_name }}
                        pattern = r"\{\{\s*" + re.escape(yml_flow_node_name + '.' + yml_flow_output.split('.')[-1]) + r"\s*\}\}"
                        value = re.sub(pattern, '{{ ' + sub_flow_output + ' }}', value)
                adjusted_params[key] = value
            node_data['params'] = adjusted_params

def validate_yaml(
    yaml_file: str,
    functions_filepath: str = None,
    structured_output_schema_filepath: str = None,
    parent_node_names: Set[str] = None,
    visited_files: Set[str] = None,
    parent_params: Set[str] = None,
    parent_node_outputs: Dict[str, List[str]] = None
) -> Tuple[bool, List[str], Dict[str, List[str]]]:
    """
    Validates the YAML data and any associated sub-flows for consistency and errors.

    Args:
        yaml_file (str): Path to the YAML file being validated.
        parent_node_names (set): Set of node names from the parent flow to detect duplicates.
        visited_files (set): Set of visited YAML file paths to prevent circular references.
        parent_params (set): Set of parameter names passed from the parent flow.
        parent_node_outputs (dict): Dictionary of node outputs from parent flows.

    Returns:
        validated (bool): True if validation passes, False otherwise.
        error_msgs (list): List of error messages.
        node_outputs (dict): Dictionary of node outputs in the current flow.
    """
    # Convert yaml_file to absolute path
    yaml_file = os.path.abspath(yaml_file)

    # Validate if functions_filepath and structured_output_schema_filepath are valid .py files
    if functions_filepath:
        if not os.path.isfile(functions_filepath):
            logger.error(f"functions_filepath '{functions_filepath}' does not exist.")
            raise FileNotFoundError(f"functions_filepath '{functions_filepath}' does not exist.")
        if os.path.splitext(functions_filepath)[1] != '.py':
            logger.error("functions_filepath must be a .py file.")
            raise ValueError("functions_filepath must be a .py file.")
    if structured_output_schema_filepath:
        if not os.path.isfile(structured_output_schema_filepath):
            logger.error(f"structured_output_schema_filepath '{structured_output_schema_filepath}' does not exist.")
            raise FileNotFoundError(
                f"structured_output_schema_filepath '{structured_output_schema_filepath}' does not exist.")
        if os.path.splitext(structured_output_schema_filepath)[1] != '.py':
            logger.error("structured_output_schema_filepath must be a .py file.")
            raise ValueError("structured_output_schema_filepath must be a .py file.")

    yaml_data = load_yaml_file(yaml_file)
    if parent_node_names is None:
        parent_node_names = set()
    if visited_files is None:
        visited_files = set()
    if parent_params is None:
        parent_params = set()
    if parent_node_outputs is None:
        parent_node_outputs = {}

    error_msgs = []
    validated = True
    logger.debug(f"Validating YAML file '{yaml_file}'")

    # Get absolute path of the yaml_file
    yaml_file_abs = os.path.abspath(yaml_file)

    # Prevent circular references
    if yaml_file_abs in visited_files:
        error_msgs.append(f"Circular reference detected in YAML file '{yaml_file}'.")
        validated = False
        return validated, error_msgs, {}
    visited_files.add(yaml_file_abs)

    # Check if yaml_data is a dictionary
    if not isinstance(yaml_data, dict):
        error_msgs.append(f"YAML file '{yaml_file}' must contain a dictionary at the top level.")
        validated = False
        return validated, error_msgs, {}

    # Check if 'nodes' key exists
    if 'nodes' not in yaml_data:
        error_msgs.append(f"YAML file '{yaml_file}' must contain a 'nodes' key.")
        validated = False
        return validated, error_msgs, {}

    nodes = yaml_data.get('nodes', [])

    # Check if 'nodes' is a list
    if not isinstance(nodes, list):
        error_msgs.append(f"The 'nodes' key in YAML file '{yaml_file}' must be a list.")
        validated = False
        return validated, error_msgs, {}

    node_names = set()
    node_outputs = {}

    for node_data in nodes:
        # Check if node_data is a dictionary
        if not isinstance(node_data, dict):
            error_msgs.append(f"A node in YAML file '{yaml_file}' is not a dictionary.")
            validated = False
            continue

        node_name = node_data.get('name')
        node_type = node_data.get('type')
        params = node_data.get('params', {})
        outputs = node_data.get('outputs', [])

        # Check for 'name' and 'type'
        if not node_name:
            error_msgs.append(f"A node in YAML file '{yaml_file}' is missing the 'name' field.")
            validated = False
            continue
        if not node_type:
            error_msgs.append(f"Node '{node_name}' in YAML file '{yaml_file}' is missing the 'type' field.")
            validated = False
            continue

        # Check for duplicate node names
        if node_name in node_names or node_name in parent_node_names:
            error_msgs.append(f"Duplicate node name '{node_name}' found in YAML file '{yaml_file}'.")
            validated = False
            continue
        else:
            node_names.add(node_name)

        # Collect node outputs
        if not isinstance(outputs, list):
            error_msgs.append(f"Outputs in node '{node_name}' must be a list in YAML file '{yaml_file}'.")
            validated = False
            continue
        else:
            node_outputs[node_name] = outputs

        # Validate node types
        valid_node_types = {'function_call', 'llm_service', 'yml_flow'}
        if node_type not in valid_node_types:
            error_msgs.append(f"Invalid node type '{node_type}' in node '{node_name}' in YAML file '{yaml_file}'.")
            validated = False
            continue

        # Node type specific validations
        if node_type == 'function_call':
            function_name = node_data.get('function')
            if not function_name:
                error_msgs.append(f"Node '{node_name}' of type 'function_call' must have a 'function' field in YAML file '{yaml_file}'.")
                validated = False
            else:
                # Validate that the function exists
                try:
                    module = load_module_from_path(functions_filepath)
                    if not hasattr(module, function_name):
                        raise AttributeError
                except (ImportError, AttributeError):
                    error_msgs.append(f"Function '{function_name}' not found in '{functions_filepath}' for node '{node_name}' in YAML file '{yaml_file}'.")
                    validated = False

        elif node_type == 'llm_service':
            service = node_data.get('service')
            if not service:
                error_msgs.append(f"Node '{node_name}' of type 'llm_service' must have a 'service' field in YAML file '{yaml_file}'.")
                validated = False
            elif service != 'openai':
                error_msgs.append(
                    f"Node '{node_name}' of type 'llm_service' references service {service} but only 'openai' is currently supported.")
                validated = False
            if 'structured_output_schema' in node_data:
                structured_output_schema_name=node_data['structured_output_schema']
                try:
                    module = load_module_from_path(structured_output_schema_filepath)
                    schema_class = getattr(module, structured_output_schema_name)
                except Exception as e:
                    error_msgs.append(f"Error importing module {structured_output_schema_filepath}: {e}")
                    validated = False
            if 'tools' in node_data:
                tools = node_data['tools']
                for i, tool in enumerate(tools):
                    # Check if COMPOSIO tools are valid
                    if tool.startswith('COMPOSIO.'):
                        tool_name = tool.split('COMPOSIO.')[1]
                        composio_toolset = ComposioToolSet()
                        try:
                            _ = composio_toolset.get_tools(actions=[tool_name])[0]
                        except Exception as e:
                            error_msgs.append(
                                f"COMPOSIO tool {tool_name} not valid. Please check COMPOSIO documentation for valid tools. \n COMPOSIO error message: {e}")
                            validated = False
                    # Check if LANGCHAIN tools are valid
                    elif tool.startswith('LANGCHAIN.'):
                        tool_name = tool.split('LANGCHAIN.')[1]
                        module = importlib.import_module('langchain_community.tools')
                        try:
                            _ = getattr(module, tool_name)
                        except:
                            error_msgs.append(
                                f"Unable to import {tool_name} from langchain_community.tools. Please check Langchain's documentation.\n Langchain error message: {e}")
                            validated = False
                    else:
                        try:
                            module = load_module_from_path(functions_filepath)
                            func = getattr(module, tool)
                        except Exception as e:
                            error_msgs.append(f"Error importing module {functions_filepath}: {e}")
                            validated=False

        elif node_type == 'yml_flow':
            yml_file_sub = node_data.get('yml_file')
            if not yml_file_sub:
                error_msgs.append(f"Node '{node_name}' of type 'yml_flow' must have a 'yml_file' field in YAML file '{yaml_file}'.")
                validated = False
                continue
            # Resolve the subflow yaml file path relative to the current yaml file
            yml_file_sub_path = os.path.abspath(os.path.join(os.path.dirname(yaml_file), yml_file_sub))
            # Check if the YAML file exists
            if not os.path.exists(yml_file_sub_path):
                error_msgs.append(f"YAML file '{yml_file_sub_path}' specified in node '{node_name}' does not exist.")
                validated = False
                continue
            # Load the sub-flow YAML file
            sub_yaml_data = load_yaml_file(yml_file_sub_path)
            # Get the 'params' passed to the sub-flow
            sub_flow_params = node_data.get('params', {})
            sub_flow_param_names = set(sub_flow_params.keys())

            # Collect all parameter names used in the sub-flow
            used_params_in_sub_flow = collect_used_params(sub_yaml_data)

            # Check that each parameter passed in is used in the sub-flow
            unused_params = sub_flow_param_names - used_params_in_sub_flow
            if unused_params:
                error_msgs.append(f"Parameters {unused_params} passed to sub-flow '{yml_file_sub_path}' are not used in the sub-flow.")
                validated = False

            # Collect all parameters used in the sub-flow but not defined
            sub_flow_parent_params = parent_params.union(sub_flow_param_names)
            undefined_params = used_params_in_sub_flow - sub_flow_param_names - sub_flow_parent_params
            if undefined_params:
                error_msgs.append(f"Sub-flow '{yml_file_sub_path}' uses undefined parameters: {undefined_params}")
                validated = False

            # Recursively validate the sub-flow
            validated_subflow, error_msgs_subflow, sub_flow_node_outputs = validate_yaml(
                yml_file_sub_path, functions_filepath, structured_output_schema_filepath,
                set(), visited_files.copy(),
                parent_params=sub_flow_parent_params, parent_node_outputs={}
            )
            if error_msgs_subflow:
                error_msgs.extend(error_msgs_subflow)
            validated = validated and validated_subflow

            # Check that outputs specified are produced by the sub-flow
            sub_flow_outputs = set()
            for outputs_list in sub_flow_node_outputs.values():
                sub_flow_outputs.update(outputs_list)
            specified_outputs = set(node_data.get('outputs', []))
            missing_outputs = specified_outputs - sub_flow_outputs
            if missing_outputs:
                error_msgs.append(f"Outputs {missing_outputs} specified in 'outputs' of 'yml_flow' node '{node_name}' are not produced by the sub-flow '{yml_file_sub_path}'.")
                validated = False
            # In 'node_outputs', for the 'yml_flow' node, store the outputs as specified
            node_outputs[node_name] = list(specified_outputs)

    # After collecting all node names and outputs, check for references to undefined nodes and outputs
    all_node_names = node_names.union(parent_node_names)
    all_node_outputs = {**parent_node_outputs, **node_outputs}

    for node_data in nodes:
        node_name = node_data.get('name')
        if not node_name:
            continue  # Skip if node_name is not defined
        params = node_data.get('params', {})
        # Collect all referenced nodes and outputs in parameters
        referenced_nodes_outputs = collect_referenced_nodes_and_outputs(params)
        for ref_node, ref_output in referenced_nodes_outputs:
            # Check if the node exists
            if ref_node not in all_node_names:
                error_msgs.append(f"Node '{node_name}' in YAML file '{yaml_file}' references undefined node '{ref_node}'.")
                validated = False
            else:
                # Check if the output exists in the referenced node
                parent_outputs = all_node_outputs.get(ref_node, [])
                if ref_output not in parent_outputs:
                    error_msgs.append(
                        f"Node '{node_name}' in YAML file '{yaml_file}' references undefined output '{ref_output}' "
                        f"from node '{ref_node}'."
                    )
                    validated = False

    # Build a temporary graph to check for cycles
    temp_graph = nx.DiGraph()
    for node_name in node_names:
        temp_graph.add_node(node_name)
    for node_data in nodes:
        node_name = node_data.get('name')
        params = node_data.get('params', {})
        referenced_nodes = collect_referenced_nodes(params)
        for ref_node in referenced_nodes:
            if ref_node in node_names:
                temp_graph.add_edge(ref_node, node_name)
    if not nx.is_directed_acyclic_graph(temp_graph):
        error_msgs.append(f"The workflow graph in YAML file '{yaml_file}' has cycles.")
        validated = False

    return validated, error_msgs, node_outputs

def collect_referenced_nodes_and_outputs(params) -> Set[Tuple[str, str]]:
    """
    Collects all node names and outputs referenced in the parameters.

    Args:
        params (dict): Parameters dictionary.

    Returns:
        Set[Tuple[str, str]]: A set of tuples containing referenced node names and outputs.
    """
    referenced_nodes_outputs = set()

    def traverse(value):
        if isinstance(value, str):
            # Extract node and output references from templated strings
            import re
            pattern = r"\{\{\s*([\w_]+)\.([^\s\}]+)\s*\}\}"
            matches = re.findall(pattern, value)
            for node_name, output_reference in matches:
                base_output_name = get_base_output_name(output_reference)
                referenced_nodes_outputs.add((node_name, base_output_name))
        elif isinstance(value, dict):
            for v in value.values():
                traverse(v)
        elif isinstance(value, list):
            for item in value:
                traverse(item)

    traverse(params)
    return referenced_nodes_outputs


def collect_used_params(yaml_data) -> Set[str]:
    """
    Collects all parameter names used in the YAML data.

    Args:
        yaml_data (dict): The YAML data.

    Returns:
        Set[str]: A set of parameter names used in the YAML data.
    """
    used_params = set()

    nodes = yaml_data.get('nodes', [])
    for node_data in nodes:
        params = node_data.get('params', {})
        used_params.update(collect_referenced_params(params))

    return used_params

def collect_referenced_params(params) -> Set[str]:
    """
    Collects all parameter names used in the parameters.

    Args:
        params (dict): Parameters dictionary.

    Returns:
        Set[str]: A set of parameter names used.
    """
    referenced_params = set()

    def traverse(value):
        if isinstance(value, str):
            # Extract parameter references from templated strings
            import re
            pattern = r"\{\{\s*([\w_]+)\s*\}\}"
            matches = re.findall(pattern, value)
            referenced_params.update(matches)
        elif isinstance(value, dict):
            for v in value.values():
                traverse(v)
        elif isinstance(value, list):
            for item in value:
                traverse(item)

    traverse(params)
    return referenced_params

def collect_referenced_nodes(params) -> Set[str]:
    """
    Collects all node names referenced in the parameters.

    Args:
        params (dict): Parameters dictionary.

    Returns:
        Set[str]: A set of referenced node names.
    """
    referenced_nodes = set()

    def traverse(value):
        if isinstance(value, str):
            # Extract node references from templated strings
            import re
            pattern = r"\{\{\s*([\w_]+)\."
            matches = re.findall(pattern, value)
            referenced_nodes.update(matches)
        elif isinstance(value, dict):
            for v in value.values():
                traverse(v)
        elif isinstance(value, list):
            for item in value:
                traverse(item)

    traverse(params)
    return referenced_nodes

def load_yaml_file(yaml_file):
    """
    Loads the YAML data from a file.

    Args:
        yaml_file (str): Path to the YAML file.

    Returns:
        dict: The YAML data.
    """
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"YAML file '{yaml_file}' does not exist.")

    with open(yaml_file, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file '{yaml_file}': {e}")
    return data

def has_yml_flow_nodes(yaml_data):
    """
    Recursively checks if the YAML data contains any 'yml_flow' nodes.

    Args:
        yaml_data (dict): The YAML data to check.

    Returns:
        bool: True if 'yml_flow' nodes are present, False otherwise.
    """
    nodes = yaml_data.get('nodes', [])
    for node_data in nodes:
        node_type = node_data.get('type')
        if node_type == 'yml_flow':
            return True
        elif node_type in ['function_call', 'llm_service']:
            continue
        else:
            # If node_type is not recognized, raise an error
            raise ValueError(f"Unknown node type '{node_type}' in node '{node_data.get('name')}'.")
    return False

def get_base_output_name(output_reference):
    """
    Extracts the base output name from an output reference.
    For example:
    - 'countries_list[i]' => 'countries_list'
    - 'output.method()' => 'output'
    """
    import re
    match = re.match(r'^([\w_]+)', output_reference)
    if match:
        return match.group(1)
    else:
        return output_reference  # Return as is if no match
