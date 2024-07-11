import os
import time
import requests
import streamlit as st
from elasticsearch import Elasticsearch
from openai import OpenAI

# Configure the OpenAI client
client = OpenAI(
    base_url='http://ollama:11434/v1/',
    api_key='ollama',
)

# Configure Elasticsearch client
es_host = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
es_client = Elasticsearch(f'http://{es_host}:9200',
                          request_timeout=60,
                          max_retries=10,
                          retry_on_timeout=True)

# Elasticsearch index settings
index_name = "course-questions"
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"}
        }
    }
}

def setup_elasticsearch_index():
    # Retry logic to wait for Elasticsearch to be ready
    retries = 10
    for i in range(retries):
        try:
            if es_client.ping():
                print("Elasticsearch is ready!")
                break
        except Exception as e:
            print(f"Attempt {i + 1} of {retries} failed: {e}")
            time.sleep(10)  # Wait for 10 seconds before retrying
    else:
        raise ConnectionError("Failed to connect to Elasticsearch after multiple retries")

    # Delete the existing index if it exists
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
        print(f"Deleted existing index: {index_name}")

    # Create the new index
    es_client.indices.create(index=index_name, body=index_settings)
    print(f"Created new index: {index_name}")

def load_and_index_documents():
    # Load and index documents
    docs_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1'
    docs_response = requests.get(docs_url)
    documents_raw = docs_response.json()

    documents = []

    for course in documents_raw:
        course_name = course['course']

        for doc in course['documents']:
            doc['course'] = course_name
            documents.append(doc)

    # Index all documents
    for doc in documents:
        es_client.index(index=index_name, body=doc)

    print("Indexed all documents successfully.")

def elastic_search(query, index_name=index_name):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs

def build_prompt(query, search_results):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    
    for doc in search_results:
        context += f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt):
    response = client.chat.completions.create(
        model='phi3',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag(query):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer

def main():
    st.title("RAG Function Invocation")

    user_input = st.text_input("Enter your input:")

    if st.button("Ask"):
        with st.spinner('Processing...'):
            try:
                output = rag(user_input)
                st.success("Completed!")
                st.write(output)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    # Setup Elasticsearch index and load documents
    print("Starting Elasticsearch setup...")
    try:
        setup_elasticsearch_index()
        print("Elasticsearch setup completed.")
    except Exception as e:
        print(f"Elasticsearch setup failed: {e}")
    
    print("Loading and indexing documents...")
    try:
        load_and_index_documents()
        print("Document indexing completed.")
    except Exception as e:
        print(f"Document indexing failed: {e}")

    main()
