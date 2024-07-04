## Prepare the environment 

__Codespace, packes, environments__
- Open a codespace, then download and install Miniconda 
- Make sure to cd .. to be in @username -> /workspaces/ directory 
```sh
wget https://repo.anaconda.com/miniconda/Miniconda3-py310_24.5.0-0-Linux-x86_64.sh
bash Miniconda3-py310_24.5.0-0-Linux-x86_64.sh
```
- After installing, open new terminal you should see (base)
- Install dependencies needed 
```sh
conda install tqdm jupyter openai elasticsearch pandas scikit-learn ipywidgets
```

__API Keys__
If you want to use OpenAi API open and follow open_ai_api_usage.ipynb notebook, note: a better way for managing keys is using direnv
```sh
sudo apt update
sudo apt install direnv 
direnv hook bash >> ~/.bashrc
```

Create / edit .envrc in your project directory
```sh
export OPENAI_API_KEY='sk-proj-key'
```

add .envrc to .gitignore 
```sh
echo ".envrc" >> .gitignore
```

allow direnv to run 
```sh
direnv allow
```

## Retrieving documents for a query 
Use a [pre-built search engine](https://github.com/alexeygrigorev/build-your-own-search-engine) and get [raw minsearch.py](https://raw.githubusercontent.com/alexeygrigorev/minsearch/main/minsearch.py)

Follow rag_intro.ipynb for further woorkflow. 

## Generating answers with OpenAI API 