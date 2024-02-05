from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import ServiceContext, VectorStoreIndex, SimpleDirectoryReader
from llama_index import set_global_service_context

from llama_index.readers import YoutubeTranscriptReader

from llama_index.readers import PDFReader

# Goals
#


urls = [
    "https://www.youtube.com/watch?v=J-7NJNqQBxw&list=PLi0evDFj8jiUQp6uRHKTyUJoU5CgnFhMl"
]

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
service_context = ServiceContext.from_defaults(embed_model=embed_model)
set_global_service_context(service_context)

# documents = YoutubeTranscriptReader().load_data(urls)
# index = VectorStoreIndex.from_documents(documents)
# query_engine = index.as_query_engine()
# response = query_engine.query(
#    "Generate 10 questions and answers from content in the lecture."
# )
# print(response)


documents = SimpleDirectoryReader(input_dir="devices").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

while True:
    response = query_engine.query(input())
    print(response)
