import ollama

res = ollama.embeddings(
    model="nomic-embed-text",
    prompt="Hello world"
)

print(len(res["embedding"]))
