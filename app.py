"""
Flask backend for JSON parser using Daytona sandbox
"""
import os
import json
import re
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
from openai import AzureOpenAI
from parser_utils import smart_json_sample, sample_large_text

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Initialize clients
daytona = Daytona(DaytonaConfig(api_key=os.getenv("DAYTONA_KEY")))
chat_client = AzureOpenAI(
    api_key=os.getenv("GPT5OMINIKEY"),
    api_version=os.getenv("OPENAI_API_VERSION_GPT_5O"),
    azure_endpoint=os.getenv("GPT5OMINIENDPOINT"),
)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/parse', methods=['POST'])
def parse_data():
    """
    Main parsing endpoint
    Expects:
    - raw_data: string (either raw JSON text or will be treated as such)
    - expected_fields: string (comma-separated field names)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        raw_data = data.get('raw_data', '')
        expected_fields = data.get('expected_fields', '')
        
        if not raw_data or not expected_fields:
            return jsonify({"error": "Both raw_data and expected_fields are required"}), 400
        
        # Step 1: Analyze the data structure
        start_time = time.time()
        
        # Determine if it's a file path or raw data
        raw_file_content = raw_data
        data_arrays = []
        
        # Try to parse as JSON to get structure
        try:
            json_data = json.loads(raw_data)
            sampled_data, data_arrays = smart_json_sample(raw_data, max_sample_items=3)
        except json.JSONDecodeError:
            # Not valid JSON, treat as text
            sampled_data = sample_large_text(raw_data)
        
        # Build array hints
        array_hints = ""
        if data_arrays:
            array_hints = "\n".join([f"- {path} contains {len(arr)} items" for path, arr in data_arrays])
        
        # Step 2: Generate parser code using LLM
        prompt = f"""Generate Python code that will parse the following raw data and extract these field informations (They may not follow the exact same name or form,
    but the general idea should be the same): {expected_fields}
    For example, if the user wants item_id, find a field that assigns some sort of id to an item.

    Data structure with samples:
    {sampled_data}

    Some potential data locations:
    {array_hints}

    Requirements:
    - The JSON data will be available in a file at: raw_data.json
    - Navigate to the correct array path in the JSON
    - Extract the requested fields: {expected_fields}
    - Return a list of dictionaries with all items from the array
    - Handle missing fields gracefully (use None)
    - Print the result as JSON using json.dumps()
    - Keep the code simple and direct

    Only output the Python code, no explanations."""
        
        llm_start = time.time()
        response = chat_client.chat.completions.create(
            model='gpt-5-mini',
            messages=[
                {"role": "system", "content": "You are a Python code generator. Output only valid Python code without any markdown formatting or explanations."},
                {"role": "user", "content": prompt}
            ]
        )
        llm_time = time.time() - llm_start
        
        generated_code = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        generated_code = re.sub(r'^```python\n|^```\n|```$', '', generated_code, flags=re.MULTILINE).strip()
        
        # Step 3: Run parser in Daytona sandbox
        params = CreateSandboxFromSnapshotParams(language="python")
        sandbox = daytona.create(params)
        
        try:
            sandbox_start = time.time()
            
            # Upload the raw data file to the sandbox
            remote_file_path = "raw_data.json"
            sandbox.fs.upload_file(raw_file_content.encode('utf-8'), remote_file_path)
            
            # Run the generated code
            result = sandbox.process.code_run(generated_code)
            sandbox_time = time.time() - sandbox_start
            
            if result.exit_code != 0:
                return jsonify({
                    "error": "Parser execution failed",
                    "details": result.result,
                    "generated_code": generated_code
                }), 500
            
            # Parse the result
            try:
                parsed_json = json.loads(result.result.strip())
            except json.JSONDecodeError:
                parsed_json = {"raw_output": result.result}
            
            total_time = time.time() - start_time
            
            return jsonify({
                "success": True,
                "data": parsed_json,
                "metadata": {
                    "total_items": len(parsed_json) if isinstance(parsed_json, list) else 1,
                    "generated_code": generated_code,
                    "timing": {
                        "total_seconds": round(total_time, 2),
                        "llm_seconds": round(llm_time, 2),
                        "sandbox_seconds": round(sandbox_time, 2)
                    }
                }
            }), 200
            
        finally:
            sandbox.delete()
            
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7001)

