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

# Custom CSS for button styling and scrollable code blocks
st.markdown("""
    <style>
    /* Style for the Parse Data button */
    div.stButton > button[kind="primary"] {
        background-color: #10b981 !important;  /* Green color */
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        font-size: 1.1rem !important;
        border-radius: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #059669 !important;  /* Darker green on hover */
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }
    
    div.stButton > button[kind="primary"]:active {
        transform: translateY(0px) !important;
    }
    
    /* Disabled state */
    div.stButton > button[kind="primary"]:disabled {
        background-color: #9ca3af !important;
        cursor: not-allowed !important;
    }
    
    /* Scrollable code blocks - limit to ~30 lines (600px height) */
    .scrollable-code pre,
    .scrollable-code code,
    .scrollable-code div[data-testid="stCode"],
    .scrollable-code div[data-testid="stCodeBlock"] {
        max-height: 600px !important;
        overflow-y: auto !important;
        overflow-x: auto !important;
    }
    
    .scrollable-code {
        max-height: 620px !important;
        overflow: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

# Backend API URL
BACKEND_URL = "http://localhost:7001"

# Title and description
st.title("🔍 Dynamic Parser")
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
# input_method = st.radio(
#     "Choose input method:",
#     ["Upload JSON File"
# #    ,"Paste Raw JSON/Text"
#     ],
#     horizontal=True
# )
input_method = "Upload JSON File" # hardocding to this. we are no longer supporting an option of 

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
            
            # Show preview with pretty printing
            with st.expander("📄 File Preview", expanded=False):
                try:
                    # Try to parse and pretty print JSON
                    json_data = json.loads(raw_data)
                    
                    # Show full JSON in scrollable container with syntax highlighting
                    with st.container(height=600):
                        st.json(json_data)
                    st.caption(f"📊 Total: {len(raw_data):,} characters | 📜 Scroll to see more")
                except json.JSONDecodeError:
                    # If not valid JSON, show as plain text in scrollable container
                    pretty_json = json.dumps(json_data, indent=2) if 'json_data' in locals() else raw_data
                    with st.container(height=600):
                        st.code(raw_data, language="text")
                    st.caption("⚠️ Not valid JSON - showing as plain text | 📜 Scroll to see more")
            
            st.success(f"✅ File loaded: {uploaded_file.name} ({len(raw_data):,} characters)")
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

# # Example suggestions
# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("💡 E-commerce Example"):
#         expected_fields = "item_name, item_id, price, UPC, image_url"
#         st.rerun()

# with col2:
#     if st.button("💡 User Data Example"):
#         expected_fields = "user_id, username, email, created_date, status"
#         st.rerun()

# with col3:
#     if st.button("💡 Product Example"):
#         expected_fields = "product_name, sku, category, stock, description"
#         st.rerun()

# Parse button
st.header("🚀 Parse Data")

if st.button("Parse Data", type="primary", disabled=not (raw_data and expected_fields)):
    if not raw_data or not expected_fields:
        st.warning("⚠️ Please provide both data and expected fields")
    else:
        # Create a status container for progress updates (log-like display)
        with st.status("🔄 Processing Request...", expanded=True) as status:
            try:
                # Step 1: Initial setup
                st.write("🚀 Starting parsing process...")
                st.write("📊 Analyzing data structure...")
                
                # Step 2: Making LLM call
                st.write("🤖 Calling LLM to generate parser code...")
                st.write("💭 LLM is analyzing your data and field requirements...")
                
                
                # Make API request
                response = requests.post(
                    f"{BACKEND_URL}/parse",
                    json={
                        "raw_data": raw_data,
                        "expected_fields": expected_fields
                    },
                    timeout=120  # 2 minute timeout
                )

                # Step 3: Creating sandbox
                st.write("📦 Creating Daytona sandbox environment...")
                
                # Step 4: File upload
                st.write("📤 Uploading file to sandbox...")
                st.write("✓ File uploaded successfully!")
                
                # Step 5: Code execution
                st.write("⚙️ Beginning code execution in sandbox...")
                st.write("🔄 Parsing data with generated code...")
                
                # Step 6: Validating
                st.write("✓ Validating output format...")
                st.write("🧹 Cleaning up sandbox...")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Mark status as complete (keep expanded)
                    st.write("✅ All steps completed successfully!")
                    status.update(label="✅ Parsing completed!", state="complete", expanded=True)
                    
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
                        st.metric("Code Execution Time", f"{timing.get('sandbox_seconds', 0)}s")
                    
                    # Display parsed data
                    st.header("📊 Parsed Results")
                    
                    parsed_data = result.get('data', [])
                    
                    # Show as table if it's a list
                    if isinstance(parsed_data, list) and parsed_data:
                        # Convert to DataFrame for better display
                        df = pd.DataFrame(parsed_data)
                        
                        # Display options
                        col1, col2, col3 = st.columns([3, 1, 1])
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
                        with col3:
                            # csv download button
                            csv_str = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_str,
                                file_name="parsed_data.csv",
                                mime="text/csv"
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
                    # Mark status as error (keep log visible)
                    st.write("❌ Error occurred during processing")
                    status.update(label="❌ Parsing failed", state="error", expanded=True)
                    
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
                st.write("⏱️ Request timed out after 120 seconds")
                status.update(label="⏱️ Request timed out", state="error", expanded=True)
                st.error("⏱️ Request timed out. The data might be too large or complex.")
            except requests.exceptions.ConnectionError:
                st.write("🔌 Failed to connect to backend")
                status.update(label="🔌 Connection error", state="error", expanded=True)
                st.error("🔌 Cannot connect to backend. Make sure the Flask server is running.")
            except Exception as e:
                st.write(f"❌ Unexpected error: {str(e)}")
                status.update(label="❌ Unexpected error", state="error", expanded=True)
                st.error(f"❌ Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Powered by Daytona Sandbox</small>
</div>
""", unsafe_allow_html=True)

