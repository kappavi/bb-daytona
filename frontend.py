"""
Streamlit frontend for JSON parser
"""
import streamlit as st
import requests
import json
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="JSON Parser with Daytona",
    page_icon="🔍",
    layout="wide"
)

# Backend API URL
BACKEND_URL = "http://localhost:7001"

# Title and description
st.title("🔍 Dynamic JSON Parser")
st.markdown("""
Parse complex JSON structures by simply specifying what fields you need. 
The AI will automatically find and extract the data for you!
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Backend URL: " + BACKEND_URL)
    
    # Health check
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend connected")
        else:
            st.error("❌ Backend error")
    except Exception as e:
        st.error("❌ Backend not reachable")
        st.caption(f"Error: {str(e)}")

# Main content
st.header("📁 Data Input")

# Input method selection
input_method = st.radio(
    "Choose input method:",
    ["Upload JSON File", "Paste Raw JSON/Text"],
    horizontal=True
)

raw_data = None

if input_method == "Upload JSON File":
    uploaded_file = st.file_uploader(
        "Upload your JSON file",
        type=['json', 'txt'],
        help="Upload a JSON file to parse"
    )
    
    if uploaded_file is not None:
        try:
            # Read the file
            raw_data = uploaded_file.read().decode('utf-8')
            
            # Show preview
            with st.expander("📄 File Preview (first 500 characters)"):
                st.code(raw_data[:500] + ("..." if len(raw_data) > 500 else ""), language="json")
            
            st.success(f"✅ File loaded: {uploaded_file.name} ({len(raw_data)} characters)")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

else:
    raw_data = st.text_area(
        "Paste your JSON or raw text here:",
        height=200,
        placeholder='{"products": [{"name": "Item 1", "price": 9.99}, ...]}'
    )
    
    if raw_data:
        st.success(f"✅ Data loaded ({len(raw_data)} characters)")

# Expected fields input
st.header("🎯 Field Configuration")
expected_fields = st.text_input(
    "What fields do you want to extract?",
    placeholder="e.g., item_name, item_id, price, UPC, image_url",
    help="Enter comma-separated field names. The AI will find matching fields even if they have different names."
)

# Example suggestions
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💡 E-commerce Example"):
        expected_fields = "item_name, item_id, price, UPC, image_url"
        st.rerun()

with col2:
    if st.button("💡 User Data Example"):
        expected_fields = "user_id, username, email, created_date, status"
        st.rerun()

with col3:
    if st.button("💡 Product Example"):
        expected_fields = "product_name, sku, category, stock, description"
        st.rerun()

# Parse button
st.header("🚀 Parse Data")

if st.button("Parse Data", type="primary", disabled=not (raw_data and expected_fields)):
    if not raw_data or not expected_fields:
        st.warning("⚠️ Please provide both data and expected fields")
    else:
        with st.spinner("🔄 Parsing data... This may take a moment..."):
            try:
                # Make API request
                response = requests.post(
                    f"{BACKEND_URL}/parse",
                    json={
                        "raw_data": raw_data,
                        "expected_fields": expected_fields
                    },
                    timeout=120  # 2 minute timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display success
                    st.success("✅ Parsing completed!")
                    
                    # Show timing information
                    metadata = result.get('metadata', {})
                    timing = metadata.get('timing', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Items", metadata.get('total_items', 'N/A'))
                    with col2:
                        st.metric("Total Time", f"{timing.get('total_seconds', 0)}s")
                    with col3:
                        st.metric("LLM Time", f"{timing.get('llm_seconds', 0)}s")
                    with col4:
                        st.metric("Sandbox Time", f"{timing.get('sandbox_seconds', 0)}s")
                    
                    # Display parsed data
                    st.header("📊 Parsed Results")
                    
                    parsed_data = result.get('data', [])
                    
                    # Show as table if it's a list
                    if isinstance(parsed_data, list) and parsed_data:
                        # Convert to DataFrame for better display
                        df = pd.DataFrame(parsed_data)
                        
                        # Display options
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(f"Data Table ({len(df)} rows)")
                        with col2:
                            # Download button
                            json_str = json.dumps(parsed_data, indent=2)
                            st.download_button(
                                label="📥 Download JSON",
                                data=json_str,
                                file_name="parsed_data.json",
                                mime="application/json"
                            )
                        
                        # Display table
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Show raw JSON in expander
                        with st.expander("🔍 View Raw JSON"):
                            st.json(parsed_data)
                    
                    else:
                        # Display as JSON if not a list
                        st.json(parsed_data)
                    
                    # Show generated code
                    with st.expander("💻 View Generated Parser Code"):
                        generated_code = metadata.get('generated_code', '')
                        st.code(generated_code, language="python")
                
                else:
                    # Display error
                    error_data = response.json()
                    st.error(f"❌ Error: {error_data.get('error', 'Unknown error')}")
                    
                    if 'details' in error_data:
                        with st.expander("Error Details"):
                            st.code(error_data['details'])
                    
                    if 'generated_code' in error_data:
                        with st.expander("Generated Code (for debugging)"):
                            st.code(error_data['generated_code'], language="python")
                            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The data might be too large or complex.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend. Make sure the Flask server is running.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Powered by Daytona Sandbox & GPT-5 Mini</small>
</div>
""", unsafe_allow_html=True)

