import os
from dotenv import load_dotenv
from groq import Groq
import httpx
# langchain-community imports to avoid deprecation warnings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import streamlit as st
import hashlib

# Load environment variables
load_dotenv()

class CompanyChatbot:
     # Initialize Groq client
        # create a custom httpx client so the Groq library does not attempt
        # to instantiate its own SyncHttpxClientWrapper with the "proxies"
        # keyword argument (httpx.Client uses "proxy" instead) which triggers
        # a TypeError with newer httpx versions.  Passing a pre-built client
        # bypasses that code path entirely.
    def __init__(self):
        http_client = httpx.Client()
        self.groq_client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
            http_client=http_client,
        )
        
        # Initialize embeddings (same as ingestion)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load vector store
        self.persist_directory = "chroma_db"
        self.vector_store = None
        self.load_vector_store()
        
        # System prompt for company context
        self.system_prompt = """You are a helpful assistant for our company. 
        Answer questions based strictly on the provided context from company documents.
        If you cannot find the answer in the context, politely say so and suggest 
        consulting the official documentation or contacting the relevant department.
        Do not make up information or use external knowledge."""
        
        # Track retrieved documents for display
        self._last_retrieved_docs = []
    
    def load_vector_store(self):
        """Load the existing vector store"""
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="company_docs"
            )
            print("Vector store loaded successfully")
        else:
            print("No vector store found. Please run ingest.py first.")
    
    def get_document_stats(self):
        """Get comprehensive statistics about indexed documents"""
        if not self.vector_store:
            return None
        
        try:
            docs = self.vector_store.get()
            total_chunks = len(docs['ids'])
            return {
                "total_chunks": total_chunks,
                "collection": "company_docs",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        except Exception as e:
            return None
    
    def search_documents(self, query, k=5):
        """Direct search in vector database"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return [{"content": doc.page_content, "score": score} for doc, score in results]
        except Exception as e:
            return []
    
    def get_sources_summary(self):
        """Get summary of sources used in last query"""
        if not hasattr(self, '_last_retrieved_docs') or not self._last_retrieved_docs:
            return "No sources retrieved yet"
        
        summary = f"Used {len(self._last_retrieved_docs)} sources:\n"
        for i, doc in enumerate(self._last_retrieved_docs, 1):
            summary += f"{i}. Relevance: {doc['score']:.3f}\n"
        return summary
    
    def export_conversation(self, messages):
        """Export conversation history to formatted text"""
        export = "=== Company Chatbot Conversation Export ===\n\n"
        for msg in messages:
            role = "You" if msg["role"] == "user" else "Assistant"
            export += f"{role}:\n{msg['content']}\n\n"
        return export
    
    def get_relevant_context_with_metadata(self, query, k=4):
        """Enhanced context retrieval with metadata"""
        if not self.vector_store:
            return "", []
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        relevant_docs = []
        metadata = []
        
        for doc, score in results:
            if score < 1.5:
                relevant_docs.append(doc)
                metadata.append({
                    "score": score,
                    "content_length": len(doc.page_content),
                    "content": doc.page_content
                })
        
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        self._last_retrieved_docs = metadata
        return context, metadata
    
    def refine_query(self, original_query):
        """Suggest refined/alternative queries"""
        alternatives = [
            f"Can you explain {original_query.lower()}?",
            f"What is the policy about {original_query.lower()}?",
            f"Tell me more about {original_query.lower()}",
            f"How does {original_query.lower()} work in our company?"
        ]
        return alternatives

    
    def chat(self, message, chat_history=None):
        """Process a chat message and return response"""
        # Get relevant context with metadata
        context, _ = self.get_relevant_context_with_metadata(message)
        
        # Prepare messages for Groq
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context from company documents:\n{context}\n\nQuestion: {message}"}
        ]
        
        # Add chat history if provided
        if chat_history:
            messages = chat_history + messages
        
        # Get response from Groq
        try:
            response = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1024,
                top_p=0.9,
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Company Knowledge Assistant",
        page_icon="🏢",
        layout="wide"
    )
    
    # Define callback function for prompt buttons
    def set_prompt(text):
        st.session_state.auto_send_prompt = text
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chatbot" not in st.session_state:
        with st.spinner("Initializing chatbot..."):
            st.session_state.chatbot = CompanyChatbot()
    
    if "auto_send_prompt" not in st.session_state:
        st.session_state.auto_send_prompt = None
    
    # Sidebar
    with st.sidebar:
        st.title("🏢 Company Knowledge Assistant")
        st.markdown("---")
        
        # Document status
        st.subheader("📚 Document Status")
        if os.path.exists("chroma_db"):
            st.success("✅ Vector Database Active")
            
            # Display vector DB statistics
            try:
                stats = st.session_state.chatbot.get_document_stats()
                if stats:
                    st.info(f"📄 {stats['total_chunks']} document chunks indexed")
                    st.caption(f"Model: {stats['embedding_model']}")
            except Exception as e:
                st.caption("Vector DB info unavailable")
        else:
            st.error("❌ No Vector Database")
            st.markdown("Please run `ingest.py` first to index documents.")
        
        st.markdown("---")
        
        # Direct Document Search
        st.subheader("🔍 Document Search")
        search_query = st.text_input("Search documents directly:")
        if search_query:
            search_results = st.session_state.chatbot.search_documents(search_query, k=3)
            if search_results:
                st.markdown("**Search Results:**")
                for i, result in enumerate(search_results, 1):
                    with st.expander(f"Result {i} (Score: {result['score']:.3f})"):
                        st.text(result['content'])
            else:
                st.info("No results found")
        
        st.markdown("---")
        
        # Conversation Tools
        st.subheader("💬 Conversation Tools")
        
        if st.button("📊 Show Conversation Stats"):
            st.info(f"Messages: {len(st.session_state.messages)}\nConversation started.")
        
        if st.button("💾 Export Chat"):
            if st.session_state.messages:
                export_text = st.session_state.chatbot.export_conversation(st.session_state.messages)
                st.download_button(
                    label="Download Conversation",
                    data=export_text,
                    file_name="chatbot_conversation.txt",
                    mime="text/plain"
                )
            else:
                st.info("No conversation to export")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Info section
        st.markdown("### ℹ️ About")
        st.markdown("""
        This assistant answers questions based on your company documents.
        
        **Features:**
        - 🔍 Vector DB search
        - 📖 Source transparency
        - 💾 Export conversations
        - 🎯 Query suggestions
        """)

    
    # Main chat area
    st.title("💬 Chat with Company Knowledge")
    
    # Display suggested queries
    st.markdown("### 💡 Quick Questions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.button("⏰ Working Hours?", on_click=set_prompt, args=("What are the working hours?",), use_container_width=True)
    with col2:
        st.button("👤 Onboarding?", on_click=set_prompt, args=("How does onboarding work?",), use_container_width=True)
    with col3:
        st.button("📋 Policies?", on_click=set_prompt, args=("What are company policies?",), use_container_width=True)
    with col4:
        st.button("🔒 Security?", on_click=set_prompt, args=("How should I report security issues?",), use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle auto-sent prompts from quick query buttons
    prompt = None
    if st.session_state.auto_send_prompt:
        prompt = st.session_state.auto_send_prompt
        st.session_state.auto_send_prompt = None
    else:
        prompt = st.chat_input("Ask a question about company documents...")
    
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Convert messages to format for chat history
                chat_history = [
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages[:-1]
                ]
                
                response = st.session_state.chatbot.chat(prompt, chat_history)
                st.markdown(response)
        
        # Display retrieved sources from vector DB
        if hasattr(st.session_state.chatbot, '_last_retrieved_docs') and st.session_state.chatbot._last_retrieved_docs:
            with st.expander("📖 Vector DB Sources & Metadata", expanded=False):
                for i, doc_info in enumerate(st.session_state.chatbot._last_retrieved_docs, 1):
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([1, 3, 1])
                        with col1:
                            st.metric("Source", f"#{i}")
                        with col2:
                            st.caption(f"**Relevance Score:** {doc_info['score']:.4f}")
                        with col3:
                            st.metric("Length", f"{doc_info['content_length']} chars")
                        
                        st.text(doc_info['content'][:300] + "..." if len(doc_info['content']) > 300 else doc_info['content'])
        
        # Show query suggestions (refined queries)
        with st.expander("💡 Try These Related Queries", expanded=False):
            suggestions = st.session_state.chatbot.refine_query(prompt)
            cols = st.columns(2)
            for i, suggestion in enumerate(suggestions):
                col_idx = i % 2
                with cols[col_idx]:
                    st.button(
                        suggestion,
                        key=f"refined_query_{i}",
                        on_click=set_prompt,
                        args=(suggestion,),
                        use_container_width=True
                    )
        
        # Add assistant message to session state
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()