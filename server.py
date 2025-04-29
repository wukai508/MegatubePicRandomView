import os
import subprocess
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from filelock import FileLock

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def is_file_updated(file_path, last_mtime):
    """检查文件是否已更新"""
    current_mtime = os.path.getmtime(file_path)
    return current_mtime > last_mtime

@app.route('/run-megatube', methods=['GET'])
def run_megatube():
    try:
        # 确保脚本路径正确
        script_path = os.path.join(os.path.dirname(__file__), 'megatube.py')
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"找不到脚本文件: {script_path}")

        # 执行脚本
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
            
        return jsonify({
            'status': 'success',
            'message': '脚本执行完成'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'wallpaper.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/update-pic-txt', methods=['POST'])
def update_pic_txt():
    try:
        data = request.get_json()
        remaining_lines = data.get('remainingLines', [])
        
        # 写入剩余行
        with open('pic.txt', 'w') as f:
            f.write('\n'.join(remaining_lines))
            
        return jsonify({'status': 'success'})
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)