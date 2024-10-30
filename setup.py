from setuptools import setup

setup(
    name='gensphere',
    version='0.1.5',
    description='Reusable components for LLM applications',
    url='https://github.com/octopus2023-inc/gensphere/',
    author='gensphere',
    author_email='octopus2023.contact@gmail.com',
    license='MIT',
    packages=['gensphere'],
    install_requires=['Jinja2',
                      'networkx',
                      'pydantic',
                      'python-dotenv',
                      'openai',
                      'composio_core',
                      'composio_openai',
                      'langchain',
                      'langchain-community',
                      'dash',
                      'dash-cytoscape'
                      ]

)
