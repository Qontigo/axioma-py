# The axioma-py SDK

**axioma-py SDK** is a Python toolkit created on top of the rest API.
It is designed to accelerate and facilitate development of applications for systems and data integration to produce advanced analytics.

## Getting the Examples

The set of example notebooks are in the "examples" folder of the axioma-py repository you have downloaded from GitHub.


## Before Running Samples


The samples reference a json file containing sets of credentials from which sessions can be created.  
The json file is found in the [credentials](./credentials) subfolder.  In order to use the samples 'as is' copy the sample.credentials.json to credentials.json and populate the details.  

e.g. for Windows:

```
cd credentials
copy sample.credentials.json credentials.json
Notepad credentials.json


```

The "with_sessions" example uses multiple users. Otherwise, only user1 is needed.
Sample data is loaded from the files in the [sample_data](sample_data)subfolder.


## Examples Information

Two modules are used to load the users and the sample data: [load_credentials.py](load_credentials.py) and [load_sample_data.py](load_sample_data.py).  

The examples are provided as Jupyter Notebooks. 

If you have installed the axioma-py SDK in a new environment, you may also need to install jupyter.

```
pip install jupyter
```

Depending how you launch jupyter, you may also need to add a python kernel for your new virtual environment which can be selected when running jupyter notebook.
```
ipython kernel install --name "bluepysdk-venv" --user
```

Then start the notebook and open the examples.

```
jupyter notebook
```

Then browse to the examples.
In the repository, a copy of each example is available as a script that can be run directly.


```
cd axiomapy/examples
python with_sessions.py
```


The examples are provided in notebooks as follows: 
(each notebook is also available in the same location through an automated conversion to a python script):

Getting started covers most of the basics: [getting started](./getting_started.ipynb)

How to use sessions: [with_sessions](./with_sessions.ipynb)

For advanced level examples: [with_axiomaapi](./with_axiomaapi.ipynb)


### For Developers

Examples of the methods of the base types [with_entitybase](./with_entitybase.ipynb)

See also [contributing.md](../../CONTRIBUTING.md)
