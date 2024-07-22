This repository contains notes and results from coding along with [DataTalksClub's LLM Zoomcamp.](https://github.com/DataTalksClub/llm-zoomcamp) It provides instructions and workflows for setting up and using various tools and models in the context of Large Language Models.

# 1. Prepare the environment 

## 1.1 Set Up Codespace and Miniconda
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

## 1.2 Manage API Keys
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

# 2 Simple search 

## 2.1 Simple search using self-built MinSearch
Retrieving documents for a query 
Use a [self-built search engine "minsearch"](https://github.com/alexeygrigorev/build-your-own-search-engine) and get [raw minsearch.py](https://raw.githubusercontent.com/alexeygrigorev/minsearch/main/minsearch.py). 

Follow [simple_rag_flow_self_built_search_engine.ipynb notebook](notebooks/simple_rag_flow_self_built_search_engine.ipynb) for further workflow. To generate answers with OpenAI API, cf. cleaned pipeline at the end of notebook. 

## 2.2 Simple search using Elasticsearch

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

# 3. Use open LLMs for RAG

## 3.1 Running LLMs Locally
The easiest way to run an LLM without a GPU is using [Ollama](https://github.com/ollama/ollama)

In order to run Ollama locally, we need a powerful machine. If you're using Codespaces, start a new codespace with options and set machine type to 4 cores. 

Install Ollama on local machine (or new Codespace)
```sh
curl -fsSL https://ollama.com/install.sh | sh
```

Start Ollama server
```sh
ollama start
```

Ollama supports a list of models available on [ollama.com/library](https://ollama.com/library). Note: You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.

In new terminal window, pull model to run it locally without GPU. Note: We use Microsoft's Phi 3 Mini with 3.8B parameters and size of 2.3GB.
```sh
ollama pull phi3
```

Run model in terminal and start playing 
```sh
ollama run phi3
```

__Use Ollama as drop-in replacement for OpenAI API__
Follow [ollama.ipynb notebook](notebooks/ollama_minsearch.ipynb). Make sure to have dependencies installed, cf. above. 

__Where to find and how to select models?__
* [HuggingFace Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
* [HuggingFace LLM Performance Leaderboard](https://huggingface.co/spaces/optimum/llm-perf-leaderboard)

## 3.2 Integrate LLMs with Elasticsearch
There are notebooks to implement models hosted on HuggingFace:
* [Google's FLAN T5](https://huggingface.co/google/flan-t5-base), use [huggingface_flan_t5.ipynb notebook](notebooks/huggingface_flan_t5.ipynb)
* [Microsoft's Phi 3 Mini](https://huggingface.co/microsoft/Phi-3-mini-128k-instruct), use [huggingface_phi_3_mini.ipynb notebook](notebooks/huggingface_phi_3_mini.ipynb)
* [Mistral's 7B Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1), use [huggingface_mistral_7b_instruct.ipynb notebook](notebooks/huggingface_mistral_7b_instruct.ipynb). One of the Mistral 7B base models is also used in [HuggingFace's LLM tutorial](https://huggingface.co/docs/transformers/en/llm_tutorial). Note, a token is needed to use the model. Generate the token inside HuggingFace and add it as Colab Secret. 


## 3.3 Ollama + Phi 3 + ElasticSearch in Docker Compose 

Create [Docker Compose YAML](docker-compose.yaml) file 

Run (be sure to be in the same dir as yaml file)
```sh
docker-compose up -d
docker ps # verify containers are running 
curl http://localhost:9200 # verify elasticsearch, get a JSON response with Elasticsearch cluster 
curl http://localhost:11434 # verify and get "Ollama is running"
```

Verify that container is running 
```sh
docker ps
```

If not done already, enter Ollama container and download model
```sh
docker exec -it ollama bash
ollama pull phi3
ollama run phi3     # to verify and interact with model 
ollama /bye         # to stop model 
```

Open Jupyter 
```sh
jupyter notebook --ip=0.0.0.0 --no-browser --allow-root
```

You might need to remove Unused Docker Images and Containers
```sh
docker system prune -a
```

To run Ollama with Phi 3 in Docker, follow [this notebook](notebooks/ollama_elasticsearch_docker.ipynb).

## 3.4 Implement RAG Pipeline with Streamlit UI 

Make sure docker-compose.yaml file is configured correctly and services are running. Note there is a different yaml for the app inside app folder 
```sh
docker-compose up -d
```

Run Streamlit. Navigate to your app directory and start the Streamlit server.
```sh
cd /workspaces/llm-zoomcamp/app
streamlit run qa_app.py
```

In case you need to rebuild
```sh
docker-compose down
docker-compose up --build
```

# 4. Vector DBs

## 4.1 Build semantic search engine using ElasticSearch 

To work with ElasticSearch, data must be organised into documents. Thus, documents.json will be used to create embeddings with a pre-trained model from HuggingFace. These embeddings will be eventually pushed into ElasticSearch index. 

Run ElasticSearch with previously used Docker container
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

For further workflow,, follow [this notebook](notebooks/demo_es.ipynb).
