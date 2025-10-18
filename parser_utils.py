"""
Utility functions for JSON parsing and sampling
"""
import json
import os


def sample_large_text(text, max_chars=12000, num_samples=4):
    """Sample from the text to avoid hitting the max context window. Divided based on num_samples"""
    length = len(text)
    if length <= max_chars:
        return text
    
    sample_size = max_chars // num_samples
    samples = []
    
    # Distribute samples evenly across the text
    for i in range(num_samples):
        # Calculate the starting position as a percentage of total length
        # For 5 samples: 0%, 20%, 40%, 60%, 80%
        position_percent = i / num_samples
        start_pos = int(position_percent * length)
        
        # Make sure we don't go past the end
        end_pos = min(start_pos + sample_size, length)
        samples.append(text[start_pos:end_pos])
    
    return "\n\n... [content omitted] ...\n\n".join(samples)


def smart_json_sample(file_path_or_text, max_sample_items=3):
    """Parse JSON and create a structure summary with samples"""
    try:
        # Try to parse as JSON
        if os.path.exists(file_path_or_text):
            with open(file_path_or_text, 'r') as f:
                data = json.load(f)
        else:
            data = json.loads(file_path_or_text)
        
        # Find arrays that look like product/item lists
        def find_arrays(obj, path=""):
            arrays = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        # This looks like a data array
                        arrays.append((new_path, value))
                    else:
                        arrays.extend(find_arrays(value, new_path))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    arrays.extend(find_arrays(item, f"{path}[{i}]"))
            return arrays
        
        data_arrays = find_arrays(data)
        
        # Create summary
        summary = {
            "structure_info": f"JSON with {len(data_arrays)} data array(s) found",
            "arrays": []
        }
        
        for path, arr in data_arrays:
            summary["arrays"].append({
                "path": path,
                "total_items": len(arr),
                "sample_items": arr[:max_sample_items],
                "note": f"Array contains {len(arr)} total items"
            })
        
        return json.dumps(summary, indent=2), data_arrays
        
    except Exception as e:
        # Fallback to text sampling if not valid JSON
        return sample_large_text(file_path_or_text), []

