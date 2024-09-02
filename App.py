from flask import Flask, request, jsonify, render_template  
from elasticsearch import Elasticsearch  
import openai  
import os  
from dotenv import load_dotenv  
import json  

# Load environment variables  
load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")  

# Initialize Flask app and Elasticsearch  
app = Flask(__name__)  
es = Elasticsearch

# Load medical documents into Elasticsearch  
def load_medical_documents():  
    with open('medicalData.json') as f:  
        documents = json.load(f)  
        for doc in documents:  
            es.index(index='medical_chatbot', id=doc['id'], body=doc)  

# Uncomment the line below to load documents on startup  
#load_medical_documents()  

@app.route('/')  
def index():  
    return render_template('index.html')  

@app.route('/chat', methods=['POST'])  
def chat():  
    user_query = request.json['query']  
    retrieved_docs = retrieve_documents(user_query)  
    context = " ".join([doc['_source']['content'] for doc in retrieved_docs])  
    response = generate_response(f"{context}\nUser: {user_query}\nBot:")  
    return jsonify({"response": response})  

def retrieve_documents(query):  
    response = es.search(index='medical_chatbot', body={  
        "query": {  
            "match": {  
                "content": query  
            }  
        }  
    })  
    return response['hits']['hits']  

def generate_response(context):  
    response = openai.ChatCompletion.create(  
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": context}]  
    )  
    return response['choices'][0]['message']['content']  

if __name__ == '__main__':  
    app.run(debug=True)