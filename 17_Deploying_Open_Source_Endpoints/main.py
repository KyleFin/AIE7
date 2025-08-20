import os
from dotenv import load_dotenv
from together import Together
from app.graphs.simple_agent import graph
from langchain_core.messages import HumanMessage
# import getpass

load_dotenv()

together_api_key = os.getenv("TOGETHER_API_KEY")
# os.environ["TOGETHER_API_KEY"] = getpass.getpass("Enter your Together API key: ")


model_endpoint = "openai/gpt-oss-20b"
# client = Together()

# response = client.chat.completions.create(
#     model=model_endpoint,
#     messages=[
#       {
#         "role": "user",
#         "content": "How much wood could a wood chuck chuck if a wood chuck could chuck wood?"
#       }
#     ]
# )
# print(response.choices[0].message.content)

def main():
    # print("Hello from 17-deploying-open-source-endpoints!")
    # graph = build_graph().compile()
    
    question = "What type of student loans are available to freshmen?"
    messages = [HumanMessage(content=question)]
    
    response = graph.invoke({"messages": messages})
    
    # Extract and display the AI response more clearly
    if "messages" in response and len(response["messages"]) > 1:
        ai_message = response["messages"][-1]  # Get the last message (AI response)
        print(f"Question: {question}")
        print(f"\nAnswer: {ai_message.content}")
    else:
        print("Response:", response)


if __name__ == "__main__":
    main()
