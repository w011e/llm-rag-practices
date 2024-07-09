# Prepare the environment 

__Codespace, packages, environments__
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
For managing keys is using direnv
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

# Retrieving documents for a query 
Use a [self-built search engine "minsearch"](https://github.com/alexeygrigorev/build-your-own-search-engine) and get [raw minsearch.py](https://raw.githubusercontent.com/alexeygrigorev/minsearch/main/minsearch.py). 

Follow [simple_rag_flow_self_built_search_engine.ipynb notebook](notebooks/simple_rag_flow_self_built_search_engine.ipynb) for further workflow. 

# Generating answers with OpenAI API 

Follow [simple_rag_flow_self_built_search_engine.ipynb notebook](notebooks/simple_rag_flow_self_built_search_engine.ipynb) for further workflow. Cf. cleaned pipeline at the end of notebook. 

# Replace self-built minsearch with Elasticsearch
Run ElasticSearch with Docker to index the documents. 
```sh
docker run -it \
    --rm \
    --name elasticsearch \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```
If the previous command doesn't work (i.e. you see "error pulling image configuration"), try to run ElasticSearch directly from Docker Hub:
```sh
docker run -it \
    --rm \
    --name elasticsearch \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    elasticsearch:8.4.3
```

If you get "Elasticsearch has quit unexpectedly", give it more RAM:
```sh
docker run -it \
    --rm \
    --name elasticsearch \
    -m 2G \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

In a new terminal window, check that service is running 
```sh
curl http://localhost:9200
```
Once docker is running, follow [simple_rag_flow_elasticsearch.ipynb notebook](notebooks/simple_rag_flow_elasticsearch.ipynb) for further workflow.

# Use Open Source LLMs in Pipeline 
There are notebooks to implement models hosted on HuggingFace:
* [Google's FLAN T5](https://huggingface.co/google/flan-t5-base), use [huggingface_flan_t5.ipynb notebook](notebooks/huggingface_flan_t5.ipynb)
* [Microsoft's Phi 3 Mini](https://huggingface.co/microsoft/Phi-3-mini-128k-instruct), use [huggingface_phi_3_mini.ipynb notebook](notebooks/huggingface_phi_3_mini.ipynb)
* [Mistral's 7B Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1), use [huggingface_mistral_7b_instruct.ipynb notebook](notebooks/huggingface_mistral_7b_instruct.ipynb). One of the Mistral 7B base models is also used in [HuggingFace's LLM tutorial](https://huggingface.co/docs/transformers/en/llm_tutorial). Note, a token is needed to use the model. Generate the token inside HuggingFace and add it as Colab Secret. 

__Where to find and how to select models?__
* [HuggingFace Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
* [HuggingFace LLM Performance Leaderboard](https://huggingface.co/spaces/optimum/llm-perf-leaderboard)

# Run Ollama locally on CPU
The easiest way to run an LLM without a GPU is using [Ollama](https://github.com/ollama/ollama)

In order to run Ollama locally, we need a powerful machine. If you're using Codespaces, start a new codespace with options and set machine type to 4 cores. 
