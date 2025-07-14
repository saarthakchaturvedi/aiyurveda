import os
import streamlit as st

def setup_openai_api_key():
    """Setup OpenAI API key for the Streamlit app"""
    
    # Check if API key is already set
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        # Try to get from Streamlit secrets
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    
    if not api_key:
        # Show setup instructions
        st.warning("""
        **OpenAI API Key Required**
        
        To use the AI chat feature, you need to set up your OpenAI API key:
        
        **Option 1: Environment Variable (Recommended)**
        ```bash
        export OPENAI_API_KEY="your-api-key-here"
        ```
        
        **Option 2: Streamlit Secrets (For deployment)**
        Create a `.streamlit/secrets.toml` file with:
        ```toml
        OPENAI_API_KEY = "your-api-key-here"
        ```
        
        **Option 3: Direct Input (Temporary)**
        Enter your API key below:
        """)
        
        # Allow direct input for testing
        api_key = st.text_input("OpenAI API Key:", type="password", help="Enter your OpenAI API key")
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("API key set successfully!")
            return api_key
        else:
            st.info("AI chat feature will be disabled until API key is provided.")
            return None
    
    return api_key

def get_api_key_status():
    """Check if API key is available"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    return api_key is not None 