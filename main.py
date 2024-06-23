# for the code to run properly, You need to install the following packages:
# pip install langchain 
# pip install boto3
# pip install streamlit
# pip install langchain-community
# pip install langchain-aws

# Import necessary modules
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_aws import BedrockLLM
import boto3
import os
import streamlit as st

# Set AWS profile
os.environ["AWS_PROFILE"] = "Yotam"

# Bedrock client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
)

# Set model id from bedrock
modelID = "anthropic.claude-v2:1"

# Create an instance of BedrockLLM
llm = BedrockLLM(
    model_id=modelID,
    client=bedrock_client,
    model_kwargs={"max_tokens_to_sample": 2000, "temperature": 0.9}
)

# Initialize conversation context using st.session_state
if 'conversation_context' not in st.session_state:
    st.session_state.conversation_context = []

# Define simple chatbot function
def simple_chatbot(language, user_input):
    global conversation_context

    # Append the user input to the conversation context
    st.session_state.conversation_context.append(user_input)

    # Join context into a single string for more coherent input
    full_input = "\n".join(st.session_state.conversation_context)


    # Define prompt template with full input (chained)
    prompt = PromptTemplate(
        input_variables=["language", "freeform_text"],
        template="You are a multilingual chatbot. Your task is to respond in {language} based on the following input:\n\n"
                 "{freeform_text}\n\n"
                 "Please ensure all your responses are in {language}."
    )

    # Create LLMChain with BedrockLLM and prompt template
    bedrock_chain = LLMChain(llm=llm, prompt=prompt)

    # Run LLMChain with language and full input context
    response = bedrock_chain({'language': language, 'freeform_text': full_input})

    # Append chatbot's response to the conversation context
    st.session_state.conversation_context.append(response['text'])

    return response

# Set Streamlit title
st.title("Yotam Personal Assistant")

# Set sidebar for language selection
language = st.sidebar.selectbox("Language", ["English", "Hebrew"])

# Initialize user_input as empty string
user_input = ""

# Set sidebar text area for user input
if language:
    user_input = st.sidebar.text_area(label="Start conversation or ask a question:", value=user_input, max_chars=100)

# Add a submit button to trigger the chatbot function
if st.sidebar.button("Submit"):
    if language and user_input:
        response = simple_chatbot(language, user_input)
        st.write('<span style="color: orange;">Question:</span>', unsafe_allow_html=True)
        st.write(user_input)
        st.write('<span style="color: lightgreen;">Answer:</span>', unsafe_allow_html=True)
        st.write(response['text'])


# Display conversation context
if len(st.session_state.conversation_context) > 2:

    st.subheader("Conversation History:")

    # Determine the end index for the loop
    end_index = len(st.session_state.conversation_context) - 2

    for i in range(0, end_index, 2):
        question = st.session_state.conversation_context[i]
        answer = st.session_state.conversation_context[i + 1]
        #Question
        st.write('<span style="color: orange;">Question:</span>', unsafe_allow_html=True)
        st.write(question)
        #Answer
        st.write('<span style="color: lightgreen;">Answer:</span>', unsafe_allow_html=True)
        st.write(answer)

