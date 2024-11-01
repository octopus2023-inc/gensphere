import yaml
import jinja2
from jinja2 import meta
import networkx as nx
import importlib
import traceback
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import openai
from openai import OpenAI
import inspect
from typing import Union, Set
from composio_openai import ComposioToolSet, App, Action
from langchain_core.utils.function_calling import convert_to_openai_function
import textwrap
# Import YamlCompose and validate_yaml
from gensphere.yaml_utils import YamlCompose, load_yaml_file, has_yml_flow_nodes, validate_yaml
from gensphere.utils import load_module_from_path

# Load environment variables
load_dotenv()


# Module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set the root logger to WARNING to suppress INFO logs from external libraries
logging.basicConfig(level=logging.ERROR)
logging.getLogger('composio').setLevel(logging.ERROR) #suppress INFO logs from composio

class GenFlow:
    """
    Class to parse YAML data, construct an execution graph, and execute nodes.
    """

    def __init__(self, yaml_file,functions_filepath=None,structured_output_schema_filepath=None):
        self.yaml_file = os.path.abspath(yaml_file)  # Path to the main YAML file
        self.functions_filepath=functions_filepath
        self.structured_output_schema_filepath=structured_output_schema_filepath
        self.yaml_data = load_yaml_file(yaml_file)
        self.nodes = {}        # Maps node names to Node instances
        self.outputs = {}      # Stores outputs from nodes
        self.graph = nx.DiGraph()
        self.env = jinja2.Environment()
        self.client = OpenAI()
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

    logger.debug("GenFlow initialized.")

    def parse_yaml(self):
        """
        Parses the YAML data and constructs nodes.
        """
        # Validate the YAML data before parsing

        validated, error_msgs, node_outputs=validate_yaml(self.yaml_file,
                                                          self.functions_filepath,
                                                          self.structured_output_schema_filepath)
        if validated:
            logger.info(f"yaml file {self.yaml_file} passed all consistency checks")
        else:
            raise Exception(f"yaml file {self.yaml_file} didn't pass consistency checks.\nError messages: {error_msgs}")

        # Check if there are any 'yml_flow' nodes
        if has_yml_flow_nodes(self.yaml_data):
            logger.info("Detected 'yml_flow' nodes. Composing YAML files using YamlCompose.")
            # Compose the YAML data into a single flow
            yml_composer = YamlCompose(self.yaml_file,self.functions_filepath,self.structured_output_schema_filepath)
            self.composed_yaml_data = yml_composer.compose()
            data = self.composed_yaml_data
        else:
            data = self.yaml_data
            logger.debug("No 'yml_flow' nodes detected. Proceeding with original YAML data.")

        logger.debug("Parsing YAML data")
        for node_data in data.get('nodes', []):
            node = Node(node_data)
            logger.debug(f"Adding node '{node.name}' of type '{node.type}'")
            if node.name in self.nodes:
                raise ValueError(f"Duplicate node name '{node.name}' found.")
            self.nodes[node.name] = node

        # Build the execution graph
        self.build_graph()

    def build_graph(self):
        logger.debug("Building execution graph")
        for node in self.nodes.values():
            self.graph.add_node(node.name)
            logger.debug(f"Added node '{node.name}' to graph")

        node_names = self.nodes.keys()
        for node in self.nodes.values():
            dependencies = node.get_dependencies(node_names)
            logger.debug(f"Node '{node.name}' dependencies: {dependencies}")
            for dep in dependencies:
                if dep in self.nodes:
                    self.graph.add_edge(dep, node.name)
                    logger.debug(f"Added edge from node '{dep}' to '{node.name}'")
                else:
                    logger.error(f"Node '{node.name}' depends on undefined node or variable '{dep}'")
                    raise ValueError(f"Node '{node.name}' depends on undefined node or variable '{dep}'.")
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            logger.error("The execution graph has cycles. Cannot proceed.")
            raise ValueError("The execution graph has cycles. Cannot proceed.")


    def run(self):
        """
        Executes the nodes in topological order.
        """
        try:
            execution_order = list(nx.topological_sort(self.graph))
            logger.info(f"Execution order: {execution_order}")
        except nx.NetworkXUnfeasible:
            logger.error("Graph has cycles, cannot proceed.")
            raise Exception("Graph has cycles, cannot proceed.")

        for node_name in execution_order:
            node = self.nodes[node_name]
            node.set_flow(self)  # Set the reference to the GenFlow instance

            # Render parameters
            try:
                logger.debug(f"Rendering parameters for node '{node_name}'")
                params = node.render_params(self.outputs, self.env)
                logger.debug(f"Parameters for node '{node_name}': {params}")
            except Exception as e:
                raise Exception(f"Error rendering params for node '{node_name}': {e}")
                traceback.print_exc()

            # Execute node
            try:
                if isinstance(params, list):
                    # We need to execute the node multiple times
                    outputs_list = []
                    for param_set in params:
                        output = node.execute(param_set)
                        # Validate output
                        if not isinstance(output, dict):
                            raise ValueError(f"Node '{node_name}' did not return a dictionary of outputs.")
                        expected_outputs = set(node.outputs)
                        actual_outputs = set(output.keys())
                        if expected_outputs != actual_outputs:
                            raise ValueError(
                                f"Node '{node_name}' outputs {actual_outputs} do not match expected outputs {expected_outputs}."
                            )
                        outputs_list.append(output)
                    # Combine outputs
                    combined_outputs = {}
                    for output_name in node.outputs:
                        combined_outputs[output_name] = [output[output_name] for output in outputs_list]
                    # Save outputs as lists
                    self.outputs[node_name] = combined_outputs
                    logger.debug(f"Outputs of node '{node_name}': {combined_outputs}")
                else:
                    outputs = node.execute(params)
                    # Validate outputs
                    if not isinstance(outputs, dict):
                        raise ValueError(f"Node '{node_name}' did not return a dictionary of outputs.")
                    expected_outputs = set(node.outputs)
                    actual_outputs = set(outputs.keys())
                    if expected_outputs != actual_outputs:
                        raise ValueError(
                            f"Node '{node_name}' outputs {actual_outputs} do not match expected outputs {expected_outputs}."
                        )
                    # Save outputs
                    logger.debug(f"Saving Outputs of node '{node_name}': {outputs}")
                    self.outputs[node_name] = outputs
            except Exception as e:
                raise Exception(f"Error executing node '{node_name}': {e}")
                traceback.print_exc()

class Node:
    """
    Represents an operation node in the execution graph.
    """

    def __init__(self, node_data):
        self.name = node_data['name']
        self.type = node_data['type']
        self.node_data = node_data
        self.outputs = node_data.get('outputs', [])
        self.flow = None  # Reference to the GenFlow instance
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    def set_flow(self, flow):
        """
        Sets the reference to the GenFlow instance.

        Args:
            flow (GenFlow): The GenFlow instance.
        """
        self.flow = flow

    def get_dependencies(self, node_names):
        dependencies = set()
        params = self.node_data.get('params', {})
        for value in params.values():
            dependencies.update(self.extract_dependencies_from_value(value, node_names))
        return dependencies

    def extract_dependencies_from_value(self, value, node_names):
        env = jinja2.Environment()
        ast = env.parse(str(value))
        variables = meta.find_undeclared_variables(ast)
        dependencies = set()
        for var in variables:
            var_parts = var.split('.')
            base_var = var_parts[0]
            if base_var in node_names:
                dependencies.add(base_var)
        return dependencies

    def render_params(self, outputs, env):
        """
        Renders the parameters with values from previous outputs.

        Args:
            outputs (dict): Outputs from previously executed nodes.
            env (jinja2.Environment): Jinja2 environment for templating.

        Returns:
            dict or list of dicts: Rendered parameters ready for execution.
        """
        import copy
        import re

        params = self.node_data.get('params', {})
        # Build the context with outputs accessible by node name
        context = {}
        for node_name, node_outputs in outputs.items():
            context[node_name] = node_outputs

        # Initialize variables
        indexed_params = {}
        iterables = {}
        # Collect all indexed references and their iterables
        for key, value in params.items():
            if isinstance(value, str):
                # Check for indexed references
                indexed_var_pattern = r"\{\{\s*([\w_\.]+)\[(.*?)\]\s*\}\}"
                matches = re.findall(indexed_var_pattern, value)
                if matches:
                    indexed_params[key] = matches  # Store matches for this parameter
                    for var_name, index_expr in matches:
                        var_parts = var_name.split('.')
                        obj = context
                        try:
                            for part in var_parts:
                                if isinstance(obj, dict):
                                    obj = obj[part]
                                else:
                                    obj = getattr(obj, part)
                            # obj should now be the iterable
                            if not hasattr(obj, '__iter__'):
                                raise ValueError(f"Variable '{var_name}' is not iterable.")
                            iterables[var_name] = obj
                        except (KeyError, AttributeError, TypeError) as e:
                            raise ValueError(f"Variable '{var_name}' not found in context.") from e

        if indexed_params:
            # Handle parameters with indexed references
            max_length = max(len(it) for it in iterables.values())
            rendered_params_list = []
            for i in range(max_length):
                # Build a context for this iteration
                iter_context = copy.deepcopy(context)
                # Update iter_context with current index values
                for var_name, iterable in iterables.items():
                    var_parts = var_name.split('.')
                    # Get value at index i or None if out of range
                    value = iterable[i] if i < len(iterable) else None
                    self.set_in_context(iter_context, var_parts, value)
                # Render parameters
                rendered_params = {}
                for key, value in params.items():
                    if isinstance(value, str):
                        # Replace indexed references in the parameter
                        param_value = value
                        matches = indexed_params.get(key, [])
                        for var_name, index_expr in matches:
                            var_parts = var_name.split('.')
                            var_value = iter_context
                            try:
                                for part in var_parts:
                                    if isinstance(var_value, dict):
                                        var_value = var_value[part]
                                    else:
                                        var_value = getattr(var_value, part)
                            except (KeyError, AttributeError, TypeError):
                                var_value = None
                            full_ref = f"{{{{ {var_name}[{index_expr}] }}}}"
                            param_value = param_value.replace(full_ref, str(var_value))
                        # Render any remaining templates
                        template = env.from_string(param_value)
                        rendered_value = template.render(**iter_context)
                        rendered_params[key] = rendered_value
                    else:
                        rendered_params[key] = value
                rendered_params_list.append(rendered_params)
            return rendered_params_list
        else:
            # No indexed parameters, proceed as before
            rendered_params = {}
            for key, value in params.items():
                if isinstance(value, str):
                    # Check if the value is a simple variable reference
                    simple_var_pattern = r"^\{\{\s*([\w_\.]+)\s*\}\}$"
                    match = re.match(simple_var_pattern, value)
                    if match:
                        var_name = match.group(1)
                        var_parts = var_name.split('.')
                        obj = context
                        try:
                            for part in var_parts:
                                if isinstance(obj, dict):
                                    obj = obj[part]
                                else:
                                    obj = getattr(obj, part)
                            rendered_params[key] = obj
                        except (KeyError, AttributeError, TypeError) as e:
                            raise ValueError(f"Variable '{var_name}' not found in context.") from e
                    else:
                        template = env.from_string(value)
                        rendered_value = template.render(**context)
                        rendered_params[key] = rendered_value
                else:
                    rendered_params[key] = value
            return rendered_params

    def set_in_context(self, context, var_parts, value):
        obj = context
        for part in var_parts[:-1]:
            if isinstance(obj, dict):
                if part not in obj:
                    obj[part] = {}
                obj = obj[part]
            else:
                if not hasattr(obj, part):
                    setattr(obj, part, {})
                obj = getattr(obj, part)
        last_part = var_parts[-1]
        if isinstance(obj, dict):
            obj[last_part] = value
        else:
            setattr(obj, last_part, value)

    def execute(self, params):
        """
        Executes the node based on its type and parameters.

        Args:
            params (dict): Parameters for the node execution.

        Returns:
            dict: Outputs from the node execution.
        """
        self.logger.info(f"Executing node '{self.name}'")
        self.logger.debug(f"Params for node '{self.name}': {params}")
        if self.type == 'function_call':
            return self.execute_function_call(params)
        elif self.type == 'llm_service':
            return self.execute_llm_service(params)
        else:
            raise NotImplementedError(f"Type '{self.type}' not implemented for node '{self.name}'.")

    def execute_function_call(self, params):
        """
        Executes a function call node.

        Args:
            params (dict): Parameters for the function.

        Returns:
            dict: Dictionary of outputs from the function.
        """
        try:
            module = load_module_from_path(self.flow.functions_filepath)
            func = getattr(module, self.node_data['function'])
        except ImportError as e:
            raise ImportError(f"Error importing module {self.flow.functions_filepath}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Function '{self.node_data['function']}' not found in {self.flow.functions_filepath} module.")

        # Check if function has proper docstrings and type annotations
        signature = inspect.signature(func)

        # Execute function with parameters
        result = func(**params)
        if not isinstance(result, dict):
            raise ValueError(f"Function '{self.node_data['function']}' should return a dictionary of outputs.")
        # Ensure result keys match outputs
        expected_outputs = set(self.outputs)
        actual_outputs = set(result.keys())
        if expected_outputs != actual_outputs:
            raise ValueError(
                f"Function outputs {actual_outputs} do not match expected outputs {expected_outputs}."
            )
        return result

    def execute_llm_service(self, params):
        """
        Executes an LLM service node.

        Args:
            params (dict): Parameters for the LLM service.

        Returns:
            dict: Dictionary of outputs from the LLM service.
        """
        service = self.node_data['service']
        if service == 'openai':
            return self.execute_openai_service(params)
        else:
            raise NotImplementedError(f"LLM service '{service}' not implemented for node '{self.name}'.")

    def execute_openai_service(self, params):
        """
        Executes an OpenAI LLM service call using the chat completions API.

        Args:
            params (dict): Parameters for the LLM service.

        Returns:
            dict: Dictionary of outputs from the LLM service.
        """
        import inspect
        model = self.node_data.get('model')
        tools = self.node_data.get('tools')
        structured_output_schema_name = self.node_data.get('structured_output_schema')

        # Check if both 'tools' and 'structured_output_schema' are defined
        if tools and structured_output_schema_name:
            raise ValueError(f"Node '{self.name}' cannot have both 'tools' and 'structured_output_schema' defined.")
        # Prepare messages
        messages = [
            {"role": "user", "content": params['prompt']}
        ]

        if tools:
            # Function calling
            # Prepare the function definitions
            function_definitions = []
            available_functions = {}
            composio_tools=[]
            langchain_tools=[]
            for tool_name in tools:
                # Register COMPOSIO tools
                if tool_name.split('.')[0]=='COMPOSIO':
                    tool_name=tool_name.split('COMPOSIO.')[1]
                    composio_toolset = ComposioToolSet()
                    composio_tools.append(tool_name)
                    self.logger.debug(f"Registering COMPOSIO tool for openai call: {tool_name}")
                    try:
                        function_schema = composio_toolset.get_tools(actions=[tool_name])[0]
                    except Exception as e:
                        print(e)
                    try:
                        func = lambda response: ComposioToolSet().handle_tool_calls(response)
                    except Exception as e:
                            print(e)
                #Register LANGCHAIN tools
                elif tool_name.split('.')[0]=='LANGCHAIN':
                    tool_name=tool_name.split('LANGCHAIN.')[1]
                    module = importlib.import_module('langchain_community.tools')
                    try:
                        langchain_tool = getattr(module, tool_name)
                    except Exception as e:
                            print(f"Unable to import {tool_name} from langchain_community.tools. Please check Langchain's documentation.\n Langchain error message: {e}")
                    self.logger.debug(f"Registering LANGCHAIN tool for openai call: {tool_name}")
                    langchain_tool_instance=langchain_tool()
                    langchain_openai_function_format=convert_to_openai_function(langchain_tool_instance)
                    function_schema={'type':'function','function':langchain_openai_function_format}
                    tool_name=function_schema['function']['name']
                    langchain_tools.append(tool_name)
                    run_langchain_tool=lambda x: langchain_tool_instance.invoke(x)
                    func=run_langchain_tool
                else:
                    try:
                        module = load_module_from_path(self.flow.functions_filepath)
                        func = getattr(module, tool_name)
                    except ImportError as e:
                        raise ImportError(f"Error importing module {self.flow.functions_filepath}: {e}")
                    except AttributeError as e:
                        raise AttributeError(f"Function '{tool_name}' not found in {self.flow.functions_filepath} module.")

                    # Check if function has proper docstrings and type annotations
                    if not func.__doc__:
                        raise ValueError(f"Function '{tool_name}' must have a docstring.")
                    signature = inspect.signature(func)
                    for param in signature.parameters.values():
                        if param.annotation == inspect.Parameter.empty:
                            raise ValueError(f"Parameter '{param.name}' in function '{func.__name__}' lacks type annotation.")

                    # Get the function schema from the function object
                    function_schema = get_function_schema(func)

                # Build the function definition
                function_definitions.append(function_schema)

                # Add to available functions
                available_functions[tool_name] = func

            # Call OpenAI API
            response = self.flow.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=function_definitions,
                tool_choice="auto"  # or "auto"
            )

            assistant_message = response.choices[0].message
            messages.append(assistant_message)

            # Check if the assistant wants to call a function
            if assistant_message.tool_calls:
                tool_calls = assistant_message.tool_calls
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call=available_functions[function_name]
                    if not function_to_call:
                        raise ValueError(f"Function '{function_name}' is not available.")
                    #Handle COMPOSIO function execution
                    if function_name in composio_tools:
                        function_response=self.handle_composio_tool_execution(response,tool_call,tool_calls,function_name,function_to_call)
                    #Handle LANGCHAIN function execution
                    elif function_name in langchain_tools:
                        function_response=self.handle_langchain_tool_execution(tool_call,function_name,function_to_call)
                    #Handle custom function execution
                    else:
                        function_args = tool_call.function.arguments
                        # Parse the arguments
                        try:
                            arguments = json.loads(function_args)
                        except json.JSONDecodeError as e:
                            raise ValueError(f"Failed to parse function arguments: {e}")
                        # Get the function signature and call the function with given arguments
                        try:
                            sig = inspect.signature(function_to_call)
                            call_args = {}
                            for k, v in sig.parameters.items():
                                if k in arguments:
                                    call_args[k] = arguments[k]
                                elif v.default != inspect.Parameter.empty:
                                    call_args[k] = v.default
                                else:
                                    raise ValueError(f"Missing required argument '{k}' for function '{function_name}'.")
                            self.logger.debug(f"Calling function '{function_name}' with arguments {call_args}")
                            function_response = function_to_call(**call_args)
                            self.logger.debug(f"Function '{function_name}' returned: {function_response}")
                        except Exception as e:
                            raise Exception(f"Error executing function '{function_name}': {e}")

                    # Append the function's response to messages
                    tool_message = {
                        "tool_call_id":tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response)
                    }
                    self.logger.debug(f'tool message{tool_message}')
                    messages.append(tool_message)

                # Call the model again to get the final response
                second_response = self.flow.client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                assistant_final_message = second_response.choices[0].message
                result = assistant_final_message.content

                if len(self.outputs) != 1:
                    raise ValueError(
                        f"Node '{self.name}' expects {len(self.outputs)} outputs, but OpenAI service returned 1."
                    )
                return {self.outputs[0]: result}

            else:
                # The assistant did not call any function
                result = assistant_message.content
                if len(self.outputs) != 1:
                    raise ValueError(
                        f"Node '{self.name}' expects {len(self.outputs)} outputs, but OpenAI service returned 1."
                    )
                return {self.outputs[0]: result}

        elif structured_output_schema_name:
            # Structured outputs
            # Get the schema from your structured_output_schema file
            try:
                module = load_module_from_path(self.flow.structured_output_schema_filepath)
                schema_class = getattr(module, structured_output_schema_name)
            except ImportError as e:
                raise ImportError(f"Error importing module {self.flow.structured_output_schema_filepath}: {e}")
            except AttributeError as e:
                raise AttributeError(f"Schema '{structured_output_schema_name}' not found in '{self.flow.structured_output_schema_filepath}' module.")


            # Call OpenAI API with response_format
            try:
                response = self.flow.client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=schema_class,
                )

                # Get the parsed result
                assistant_message = response.choices[0].message
                if assistant_message.refusal:
                    raise Exception(f"OpenAI refusal for structured outputs on node '{self.name}'. Refusal:{assistant_message.refusal}")
                else:
                    result = assistant_message.parsed
            except Exception as e:
                if type(e) == openai.LengthFinishReasonError:
                    raise Exception(f"Too many tokens were passed to openAi during structured output generation on node {self.name}")
                else:
                    raise Exception(f"Failed to parse structured output for node '{self.name}'. {e}")
            if result is None:
                raise ValueError(f"Failed to parse structured output for node '{self.name}'. result coming as None")

            if len(self.outputs) != 1:
                raise ValueError(
                    f"Node '{self.name}' expects {len(self.outputs)} outputs, but OpenAI service returned 1."
                )
            return {self.outputs[0]: result}

        else:
            # Simple prompt completion
            response = self.flow.client.chat.completions.create(
                model=model,
                messages=messages
            )
            assistant_message = response.choices[0].message
            result = assistant_message.content
            if len(self.outputs) != 1:
                raise ValueError(
                    f"Node '{self.name}' expects {len(self.outputs)} outputs, but OpenAI service returned 1."
                )
            return {self.outputs[0]: result}

    def handle_composio_tool_execution(self,tool_call_response,tool_call,tool_calls,function_name,function_to_call):
        """
        Executes COMPOSIO tools by parsing LLM response.

        Args:
            tool_call_response: LLM response object containing tool call arguments
            tool_call: COMPOSIO tool call object from tool_call_response
            tool_calls: All tool calls from LLM response
            function_name: registered name COMPOSIO function to be executed
            function_to_call: COMPOSIO function to be executed

        Returns:
            function_response: Output of COMPOSIO function
        """

        edited_response = tool_call_response
        edited_response.choices[0].message.tool_calls = [tool_call]
        self.logger.debug(f"Executing COMPOSIO tool: {function_name}")
        function_response = function_to_call(edited_response)
        edited_response.choices[0].message.tool_calls = tool_calls

        return function_response

    def handle_langchain_tool_execution(self,tool_call,function_name,function_to_call):
        """
        Executes LANGCHAIN tools by parsing LLM response.

            Args:
                tool_call: LANGCHAIN tool call object from tool_call_response
                function_name: registered name of LANGCHAIN function to be executed
                function_to_call: LANGCHAIN function to be executed

            Returns:
                function_response: Output of LANGCHAIN function
        """
        try:
            function_args = tool_call.function.arguments
            arguments = json.loads(function_args)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse function arguments: {e}")
        self.logger.debug(f"Executing langchain tool '{function_name}'.")
        try:
            self.logger.debug(f"Calling function '{function_name}' with arguments {arguments}")
            function_response = function_to_call(arguments)
            self.logger.debug(f"Langchain function '{function_name}' returned: {function_response}")
            return function_response
        except Exception as e:
            raise Exception(f"Error executing langchain function '{function_name}': {e}")

def get_function_schema(func):
    """
    Retrieves the function schema for a function object by inspecting its signature and docstring.

    Args:
        func (function): The function object.

    Returns:
        dict: The function definition, including name, description, parameters.
    """
    import inspect

    function_name = func.__name__
    docstring = inspect.getdoc(func) or ""
    signature = inspect.signature(func)

    # Build parameters schema
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }

    for param_name, param in signature.parameters.items():
        param_type = param.annotation
        if param_type == inspect.Parameter.empty:
            raise ValueError(f"Parameter '{param_name}' in function '{function_name}' is missing type annotation.")

        # Handle typing.Optional and typing.Union
        if getattr(param_type, '__origin__', None) is Union:
            # Get the non-None type
            param_type = [t for t in param_type.__args__ if t is not type(None)][0]

        if hasattr(param_type, '__origin__') and param_type.__origin__ == list:
            item_type = param_type.__args__[0]
            item_type_name = type_mapping.get(item_type, "string")
            param_schema = {
                "type": "array",
                "items": {"type": item_type_name}
            }
        else:
            param_type_name = type_mapping.get(param_type, "string")
            param_schema = {
                "type": param_type_name
            }

        # Optionally, extract parameter description from docstring (not implemented here)

        parameters["properties"][param_name] = param_schema

        if param.default == inspect.Parameter.empty:
            parameters["required"].append(param_name)

    function_def = {"type": "function",
                    "function": {
                        "name": function_name,
                        "description": docstring,
                        "parameters": parameters
                                }
                    }

    return function_def
