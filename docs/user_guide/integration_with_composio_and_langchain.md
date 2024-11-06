## 4. Integrations with Composio and Langchain

GenSphere supports integration with external tools and platforms to enhance your workflows.

### 4.1 Composio Tools

[Composio](https://composio.dev/) provides a set of tools that can be used within your GenSphere workflows.

#### Using Composio Tools

- Refer to Composio tools in the `tools` field with the syntax `COMPOSIO.tool_name`.
- Ensure you have set your `COMPOSIO_API_KEY` in your environment variables.

**Example YAML Node:**

```yaml
- name: web_scraping
  type: llm_service
  service: openai
  model: "gpt-4"
  tools:
    - COMPOSIO.FIRECRAWL_SCRAPE
  params:
    prompt: |
      Scrape the content from the following URL:
      {{ url_to_scrape }}
  outputs:
    - scraped_content
```

### 4.2 LangChain Tools

[LangChain](https://langchain.com) offers a suite of tools for building applications with language models.

#### Using LangChain Tools

- Refer to LangChain tools in the `tools` field with the syntax `LANGCHAIN.tool_name`.
- Ensure the required LangChain packages are installed.

**Example YAML Node:**

```yaml
- name: data_analysis
  type: llm_service
  service: openai
  model: "gpt-4"
  tools:
    - LANGCHAIN.PandasDataFrameAnalyzer
  params:
    prompt: |
      Analyze the following data:
      {{ data_frame }}
  outputs:
    - analysis_result
```

### 4.3 Custom Tools

You can also use custom functions as tools in **llm_service** nodes.

**Example:**

```yaml
- name: custom_tool_usage
  type: llm_service
  service: openai
  model: "gpt-4"
  tools:
    - my_custom_function
  params:
    prompt: |
      Use the custom function to process the data.
  outputs:
    - custom_tool_output
```

Ensure `my_custom_function` is defined in your functions file.

---

