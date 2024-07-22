import streamlit as st
import time
from openai import OpenAI
from elasticsearch import Elasticsearch
import json
from pathlib import Path

# Initialize clients
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
    )

es_client = Elasticsearch("http://localhost:9200")

index_name = "course-questions"
home_dir = Path.cwd().parent
documents_path = home_dir / "notebooks" / "documents.json"

# Define index settings and mappings
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

# Check if the index exists
if not es_client.indices.exists(index=index_name):
    # Create the index if it does not exist
    es_client.indices.create(index=index_name, body=index_settings)
    print(f"Index '{index_name}' created.")
else:
    print(f"Index '{index_name}' already exists.")

# Load documents from JSON file
docs_raw = []
try:
    with open(documents_path, 'rt') as f_in: 
        docs_raw = json.load(f_in)
except FileNotFoundError:
    print("The file 'documents.json' was not found.")
except json.JSONDecodeError:
    print("Error decoding JSON from the file.")

# Prepare documents for indexing
if docs_raw:
    documents = []
    for course_dict in docs_raw: 
        for doc in course_dict['documents']:
            doc['course'] = course_dict['course']
            documents.append(doc)

    # Index all documents
    for doc in documents:
        es_client.index(index=index_name, body=doc)

def elastic_search(query):
    if documents:
        search_query = {
            "size": 5,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["question^3", 
                                    "text", 
                                    "section"],
                            "type": "best_fields"
                        }
                    },
                    # this is optional to filter e.g. for specific courses 
                    # "filter": {
                    #     "term": {
                    #         "course": "data-engineering-zoomcamp"
                    #     }
                    # }
                }
            }
        }
        response = es_client.search(index=index_name, 
                                    body=search_query)
        result_docs = []
        for hit in response['hits']['hits']:
            result_docs.append(hit['_source'])
        return result_docs
    else:
        print("No documents found in the index.")
        return []

def build_prompt(query, search_results): 

    prompt_template = """  

    You're a course teaching assistant.
    
    Answer the QUESTION based on the CONTEXT from the FAQ database.

    Use only the facts from the CONTEXT when answering the QUESTION.

    If you can not answer the QUESTION based on the CONTEXT, inform the user.  
        
    QUESTION: {question}
    
    CONTEXT: {context}
    """.strip()

    context = ""

    for doc in search_results: 
        context = context + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"

    return prompt_template.format(question = query, 
                                  context = context).strip()

def llm(prompt):
    response = client.chat.completions.create(
        model = 'phi3',
        messages = [{                 
            "role": "user", 
            "content": prompt
        }])

    return response.choices[0].message.content

def rag(query):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    return llm(prompt)

def main():
    st.title("RAG Demo")

    user_input = st.text_input("Please enter your query:",
                               placeholder="Type your question here...")

    if st.button("Ask"):
        with st.spinner("Processing..."):
            output_text = rag(user_input)
            st.success("Completed!")
            st.write(output_text)

if __name__ == "__main__":
    main()
    