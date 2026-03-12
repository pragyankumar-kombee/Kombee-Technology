import os
from dotenv import load_dotenv
# use langchain_community to avoid deprecated top-level imports
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class DocumentIngestor:
    def __init__(self):
        self.documents_dir = "documents"
        self.persist_directory = "chroma_db"
        
        # Initialize embeddings (using HuggingFace for free)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
    def load_documents(self):
        """Load documents from the documents directory"""
        documents = []
        
        # Load text files
        if os.path.exists(os.path.join(self.documents_dir, "txt")):
            text_loader = DirectoryLoader(
                os.path.join(self.documents_dir, "txt"),
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents.extend(text_loader.load())
        
        # Load PDF files
        if os.path.exists(os.path.join(self.documents_dir, "pdf")):
            pdf_loader = DirectoryLoader(
                os.path.join(self.documents_dir, "pdf"),
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(pdf_loader.load())
        
        # If no subdirectories, load from main documents folder
        if not documents and os.path.exists(self.documents_dir):
            # Try loading all .txt files
            txt_loader = DirectoryLoader(
                self.documents_dir,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents.extend(txt_loader.load())
            
            # Try loading all .pdf files
            pdf_loader = DirectoryLoader(
                self.documents_dir,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(pdf_loader.load())
        
        return documents
    
    def split_documents(self, documents):
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, chunks):
        """Create and persist vector store"""
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="company_docs"
        )
        
        vector_store.persist()
        print(f"Vector store created and persisted at {self.persist_directory}")
        return vector_store
    
    def ingest(self):
        """Main ingestion pipeline"""
        print("Loading documents...")
        documents = self.load_documents()
        
        if not documents:
            print("No documents found in the 'documents' directory!")
            print("Please add your company documents (PDF or TXT) to the 'documents' folder.")
            return None
        
        print(f"Loaded {len(documents)} documents")
        
        print("Splitting documents into chunks...")
        chunks = self.split_documents(documents)
        
        print("Creating vector store...")
        vector_store = self.create_vector_store(chunks)
        
        print("✅ Ingestion complete!")
        return vector_store

if __name__ == "__main__":
    ingestor = DocumentIngestor()
    
    # Create documents directory if it doesn't exist
    os.makedirs("documents", exist_ok=True)
    os.makedirs(os.path.join("documents", "txt"), exist_ok=True)
    os.makedirs(os.path.join("documents", "pdf"), exist_ok=True)
    
    print("=" * 50)
    print("Company Document Ingestion System")
    print("=" * 50)
    print("\nPlace your documents in:")
    print("  - /documents/txt/ for text files")
    print("  - /documents/pdf/ for PDF files")
    print("  - /documents/ for mixed files")
    print("\nStarting ingestion...\n")
    
    ingestor.ingest()