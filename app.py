from flask import Flask, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

TIMEOUT_SECONDS = 5

@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code","")
    lang = data.get("lang","")
    
    if  not code:
        return jsonify({"error":"No code provided"})
    
    filename = None
    
    try: 
        if "python" in  lang.lower():
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
                 f.write(code)
                 filename = f.name
                 
            cmd = ["python3", filename]
            
        elif lang.lower() == "go":
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".go", mode="w") as f:
                  f.write(code)
                  filename = f.name
            cmd = ["go","run", filename]    
        else:
            return jsonify({"error": "Unsupported language"})   
        
        result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS
        ) 
        
        return jsonify({
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout exceeded"})   
    
    finally:
        if filename and  os.path.exists(filename):
            os.remove(filename)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)