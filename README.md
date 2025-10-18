# JSON Parser Web Application

A dynamic JSON parser that uses AI to automatically extract specified fields from complex JSON structures, powered by Daytona sandbox and GPT-5 Mini.

## Architecture

- **Backend**: Flask API (`app.py`)
- **Frontend**: Streamlit UI (`frontend.py`)
- **Utils**: Helper functions (`parser_utils.py`)

## Features

- 📁 Upload JSON files or paste raw JSON/text
- 🎯 Specify fields to extract (AI finds them automatically)
- 🔍 Smart JSON structure detection
- ⚡ Secure execution in Daytona sandbox
- 📊 Beautiful table visualization with Pandas
- 💾 Download results as JSON

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Make sure your `.env` file contains:

```env
DAYTONA_KEY=your_daytona_api_key
GPT5OMINIKEY=your_azure_openai_key
OPENAI_API_VERSION_GPT_5O=your_api_version
GPT5OMINIENDPOINT=your_azure_endpoint
```

## Running the Application

### Terminal 1 - Start the Flask Backend

```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Terminal 2 - Start the Streamlit Frontend

```bash
streamlit run frontend.py
```

The frontend will open in your browser (usually `http://localhost:8501`)

## Usage

1. **Choose Input Method**:
   - Upload a JSON file, or
   - Paste raw JSON/text

2. **Specify Expected Fields**:
   - Enter comma-separated field names
   - Example: `item_name, item_id, price, UPC, image_url`
   - The AI will find matching fields even if they have different names

3. **Click "Parse Data"**:
   - Wait for processing (usually 10-30 seconds)
   - View results in a table format
   - Download as JSON if needed

## Example Use Cases

### E-commerce Data
```
Fields: item_name, item_id, price, UPC, image_url
```

### User Data
```
Fields: user_id, username, email, created_date, status
```

### Product Catalog
```
Fields: product_name, sku, category, stock, description
```

## How It Works

1. **Data Analysis**: The system samples your JSON to understand its structure
2. **Code Generation**: GPT-5 Mini generates Python parsing code
3. **Secure Execution**: Code runs in an isolated Daytona sandbox
4. **Results**: Parsed data is returned and displayed beautifully

## API Endpoints

### Health Check
```
GET /health
```

### Parse Data
```
POST /parse
Content-Type: application/json

{
  "raw_data": "your json string here",
  "expected_fields": "field1, field2, field3"
}
```

## Troubleshooting

### Backend Not Reachable
- Make sure Flask is running on port 5000
- Check if the port is already in use

### Parsing Errors
- Verify your JSON is valid
- Check the generated code in the error details
- Ensure Daytona API key is valid

### Timeout Errors
- Large files may take longer to process
- Consider reducing the data size or simplifying the structure

## File Structure

```
bb-daytona/
├── app.py              # Flask backend
├── frontend.py         # Streamlit frontend
├── parser_utils.py     # Helper functions
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README_APP.md      # This file
```

## Notes

- The application uses Daytona sandboxes for secure code execution
- Each parse request creates a new sandbox that's cleaned up afterward
- Processing time depends on data size and complexity
- Generated parser code is shown for transparency and debugging

