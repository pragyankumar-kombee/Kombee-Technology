from app import CompanyChatbot

def test_chatbot():
    chatbot = CompanyChatbot()
    
    if not chatbot.vector_store:
        print("❌ Vector store not loaded. Run ingest.py first.")
        return
    
    print("🤖 Company Chatbot Test")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("\nYou: ")
        if question.lower() == 'quit':
            break
        
        response = chatbot.chat(question)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    test_chatbot()