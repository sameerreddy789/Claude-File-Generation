import sys
import os
import re
import subprocess
import tempfile

def redirect_paths(content, workspace_dir):
    workspace_dir_clean = workspace_dir.replace('\\', '/')
    
    # Matches "/mnt/user-data/outputs/...", "/mnt/user-data/...", "/home/claude/...", "/home/user/...", "/tmp/..."
    patterns = [
        r'["\']/mnt/user-data/outputs/([^"\']+)["\']',
        r'["\']/mnt/user-data/([^"\']+)["\']',
        r'["\']/home/claude/([^"\']+)["\']',
        r'["\']/home/user/([^"\']+)["\']',
        r'["\']/tmp/([^"\']+)["\']',
    ]
    for pattern in patterns:
        content = re.sub(pattern, f'"{workspace_dir_clean}/\\1"', content)
    return content

def patch_js_code(content, workspace_dir):
    return redirect_paths(content, workspace_dir)

def patch_code(content, workspace_dir):
    # 1. Redirect paths
    content = redirect_paths(content, workspace_dir)
    
    # 2. Swap thickness and color in ReportLab TableStyle line commands
    # Matches patterns like ('LINEBEFORE', (0,0), (0,-1), C_ACCENT, 5) and swaps to 5, C_ACCENT
    line_commands = ['LINEBEFORE', 'LINEAFTER', 'LINEABOVE', 'LINEBELOW', 'GRID', 'BOX', 'INNERGRID']
    for cmd in line_commands:
        pattern = rf"\(\s*'{cmd}'\s*,\s*(\([^)]+\))\s*,\s*(\([^)]+\))\s*,\s*([^,]+)\s*,\s*([0-9.]+)\s*\)"
        content = re.sub(pattern, rf"('{cmd}', \1, \2, \4, \3)", content)

    # 3. Remove invalid ('LINEAFTER', ..., False)
    # Matches patterns like ('LINEAFTER', (0,0), (0,-1), False)
    pattern_lineafter_false = r"\(\s*'LINEAFTER'\s*,\s*\([^)]+\)\s*,\s*\([^)]+\)\s*,\s*False\s*\),?\s*\n?"
    content = re.sub(pattern_lineafter_false, "", content)

    # 4. Inject KeepTogether setStyle monkey-patch
    monkey_patch = """
# --- AUTOMATIC ANTIGRAVITY MONKEY-PATCH FOR KEEPTOGETHER SETSTYLE ---
try:
    from reportlab.platypus import KeepTogether
    if not hasattr(KeepTogether, 'setStyle'):
        def _KeepTogether_setStyle(self, style):
            for attr in ('_flowables', 'flowables'):
                lst = getattr(self, attr, None)
                if lst and len(lst) > 0 and hasattr(lst[0], 'setStyle'):
                    lst[0].setStyle(style)
                    return
        KeepTogether.setStyle = _KeepTogether_setStyle
except ImportError:
    pass
# ---------------------------------------------------------------------
"""
    content = monkey_patch + "\n" + content

    return content

def check_and_install_node_deps(code_content, workspace_dir):
    # Find all require statement packages
    requires = re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', code_content)
    
    # Standard Node.js built-ins to ignore
    builtins = {
        'fs', 'path', 'child_process', 'os', 'http', 'https', 'util', 'crypto', 
        'stream', 'events', 'readline', 'dns', 'net', 'tls', 'zlib', 'url', 
        'querystring', 'punycode', 'assert', 'buffer', 'constants', 'module'
    }
    
    external_packages = []
    for pkg in requires:
        if pkg not in builtins and not pkg.startswith('.') and not pkg.startswith('/') and not pkg.startswith('\\'):
            # Extract base package name (e.g. "react-icons/fa" -> "react-icons")
            base_pkg = pkg.split('/')[0]
            if base_pkg not in external_packages:
                external_packages.append(base_pkg)
                
    if not external_packages:
        return
        
    print(f"Detected external npm dependencies: {', '.join(external_packages)}")
    
    for pkg in external_packages:
        print(f"Checking if '{pkg}' is installed...")
        # Check using Node's module resolution (exits with 0 if found)
        check_res = subprocess.run(
            ["node", "-e", f"require('{pkg}')"], 
            cwd=workspace_dir, 
            capture_output=True, 
            text=True
        )
        if check_res.returncode != 0:
            print(f"npm package '{pkg}' is missing. Installing it...")
            install_res = subprocess.run(
                f"npm install {pkg}", 
                cwd=workspace_dir, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if install_res.returncode == 0:
                print(f"Successfully installed '{pkg}'.")
            else:
                print(f"Error installing '{pkg}':\n{install_res.stderr}")
                sys.exit(1)
        else:
            print(f"'{pkg}' is already installed.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python compile_script.py <path_to_script>")
        sys.exit(1)

    input_script = sys.argv[1]
    if not os.path.exists(input_script):
        print(f"Error: Script not found at {input_script}")
        sys.exit(1)

    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    _, ext = os.path.splitext(input_script)
    
    print(f"Reading target script: {input_script}...")
    with open(input_script, 'r', encoding='utf-8') as f:
        code_content = f.read()

    if ext.lower() == '.js':
        print("Detected JavaScript (Node.js) script.")
        
        # Auto-check and install any missing npm dependencies
        check_and_install_node_deps(code_content, workspace_dir)
        
        print("Applying path patches...")
        patched_code = patch_js_code(code_content, workspace_dir)
        
        # Create temp JS file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.js', dir=workspace_dir)
        os.close(temp_fd)
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(patched_code)
                
            print("Executing script using Node.js...")
            result = subprocess.run(["node", temp_path], capture_output=True, text=True, cwd=workspace_dir)
            
            if result.returncode == 0:
                print("\n[SUCCESS] Output details:")
                print(result.stdout)
            else:
                print("\n[ERROR] Error executing script:")
                print("--- Standard Output ---")
                print(result.stdout)
                print("--- Error Output ---")
                print(result.stderr)
                sys.exit(result.returncode)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    else:
        # Assume Python script
        print("Detected Python script.")
        print("Applying ReportLab and path patches...")
        patched_code = patch_code(code_content, workspace_dir)

        # Create a temporary file to run the patched script
        temp_fd, temp_path = tempfile.mkstemp(suffix='.py', dir=workspace_dir)
        os.close(temp_fd)

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(patched_code)

            print(f"Executing patched code using virtual environment...")
            python_exe = os.path.join(workspace_dir, ".venv", "Scripts", "python.exe")
            if not os.path.exists(python_exe):
                python_exe = sys.executable

            result = subprocess.run([python_exe, temp_path], capture_output=True, text=True, cwd=workspace_dir)

            if result.returncode == 0:
                print("\n[SUCCESS] Output details:")
                print(result.stdout)
            else:
                print("\n[ERROR] Error executing script:")
                print("--- Standard Output ---")
                print(result.stdout)
                print("--- Error Output ---")
                print(result.stderr)
                sys.exit(result.returncode)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    main()
