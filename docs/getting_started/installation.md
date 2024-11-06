# Installation

Welcome to the GenSphere documentation! This section will guide you through the installation process of GenSphere and its necessary dependencies.

## Prerequisites

Before installing GenSphere, ensure that your system meets the following prerequisites:

### 1. Python

- **Version**: Python 3.10 or higher is required.
- **Installation**:
  - **Windows**: Download and install Python from the [official website](https://www.python.org/downloads/windows/).
  - **macOS**: Python is pre-installed on macOS. However, it's recommended to install the latest version using [Homebrew](https://brew.sh/):
    ```bash
    brew install python
    ```
  - **Linux**: Use your distribution's package manager. For example, on Ubuntu:
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```

### 2. API Keys

GenSphere integrates with various external services that require API keys. Ensure you have the following:

- **OpenAI API Key**: Sign up and obtain an API key from [OpenAI](https://platform.openai.com/account/api-keys).
- **Composio API Key** (optional): If you plan to use Composio tools, obtain an API key from [Composio](https://composio.dev/). Follow the Composio documentation to understand how to add services to your account.

## Installation Steps

Follow these steps to install GenSphere and its dependencies:

### 1. Create a Virtual Environment (Recommended)

It's recommended to create a virtual environment to manage your project's dependencies. Open a terminal command window and type:

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate

# On macOS and Linux
source venv/bin/activate
```

### 2. Upgrade pip

Ensure that you have the latest version of `pip`.

```bash
pip install --upgrade pip
```

### 3. Install GenSphere

Install GenSphere using `pip`.

```bash
pip install gensphere
```

**Note**: If you encounter permission issues, you may need to use `pip` with `--user` or consider using a virtual environment as shown above.

### 4. Verify the Installation

To verify that GenSphere has been installed correctly, you can perform a simple test by importing GenSphere in Python.

```python
python -c "import gensphere; print('GenSphere installed successfully!')"
```

If the installation was successful, you should see the following output:

```
GenSphere installed successfully!
```

## Additional Dependencies

Depending on your project's requirements, you might need to install additional dependencies. 

## Troubleshooting

If you encounter any issues during installation, consider the following steps:

1. **Check Python Version**: Ensure you're using Python 3.10 or higher.
2. **Upgrade pip**: Make sure `pip` is up to date.
3. **Virtual Environment**: Use a virtual environment to avoid dependency conflicts.
4. **Contact Support**: If you're still having trouble,join our [Discord server](https://discord.gg/DZFWMXJv).

---

Proceed to the [Quickstart Guide](quickstart.md) to begin creating and running your first GenSphere workflow!