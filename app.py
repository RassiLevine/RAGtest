from flask import Flask, request, jsonify
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

app = Flask(__name__)

# Initialize Pinecone
pc = Pinecone(api_key="YOUR_API_KEY")  # Replace with your Pinecone API key
index = pc.Index("YOUR_INDEX_NAME")  # Replace with your index name

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="thenlper/gte-small",
    multi_process=True,
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize+embeddings": True},
)

# Initialize language model
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    "HuggingFaceH4/zephyr-7b-beta", quantization_config=bnb_config
)
tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta")
llm_model = pipeline(
    model=model,
    tokenizer=tokenizer,
    task="text-generation",
    do_sample=True,
    temperature=0.2,
    max_new_tokens=500,
)

# Define prompt template
prompt = """
<|system|>
You are a helpful assistant that answers on medical questions based on the real information provided from differenct sources and in the context.
Give rational and well writeen response. If you dont have proper info in the context, answer "I don't know".
Respond only to the question asked.

<|user|>
Context:
{}
---
Here is the question you need to answer.

Quesiton:{}
<|assistant|>
"""


@app.route("/api/answer", methods=["POST"])
def answer_question():
    user_input = request.json["question"]

    # Get relevant context from Pinecone
    vectorized_input = embedding_model.embed_query(user_input)
    context = index.query(
        namespace="ns1",
        vector=vectorized_input,
        top_k=1,
        include_metadata=True,
    )

    # Generate answer using language model
    answer = llm_model(prompt.format(context["matches"][0]["metadata"]["text"], user_input))

    return jsonify({"answer": answer[0]["generated_text"]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)