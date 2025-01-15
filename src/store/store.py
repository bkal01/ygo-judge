import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def load_documents(directory_path: str, glob_pattern: str = "**/*.txt"):
    """
    Load all text files from a directory and its subdirectories.
    
    Args:
        directory_path: Path to the directory containing text files
        glob_pattern: Pattern to match files (default: all .txt files in all subdirectories)
    
    Returns:
        List of loaded documents
    """
    loader = DirectoryLoader(
        directory_path,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={'autodetect_encoding': True}
    )
    
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
    
    return documents

def process_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split documents into chunks and create embeddings.
    
    Args:
        documents: List of loaded documents
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    
    Returns:
        Vector store containing the processed documents
    """
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks")
    
    embeddings = OpenAIEmbeddings(
        api_key=os.getenv("MODEL_API_KEY"),
    )
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    return vectorstore