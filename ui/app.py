import streamlit as st
from src.generation.generator import generate_response

#Page Configuration
st.set_page_config(page_title='Fintech RAG', layout="centered")
st.title("Fintech RAG application")


# 2. Initialize Chat History (So messages don't disappear)
if "messages" not in st.session_state:
    st.session_state.messages = []


# 3. Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 4. Handle User Input
if query := st.chat_input("Please ask a financial question..."):
    
    # Display user message in chat container
    with st.chat_message("user"):
        st.markdown(query)
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": query})

    # 5. Generate and Display Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing financial records..."):
            # Call your generation logic
            response = generate_response(query)
            st.markdown(response)
    
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})



    
