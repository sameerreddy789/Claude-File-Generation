import sys
import os
import re
import subprocess
import tempfile

def patch_code(content, workspace_dir):
    # 1. Redirect mnt paths to the local workspace directory
    workspace_dir_clean = workspace_dir.replace('\\', '/')
    
    # Matches "/mnt/user-data/outputs/filename.ext" or "/mnt/user-data/filename.ext"
    content = re.sub(r'["\']/mnt/user-data/outputs/([^"\']+)["\']', 
                     f'"{workspace_dir_clean}/\\1"', content)
    content = re.sub(r'["\']/mnt/user-data/([^"\']+)["\']', 
                     f'"{workspace_dir_clean}/\\1"', content)
    
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
    # This solves the story[-1].setStyle(...) crash by delegating setStyle to the Table inside KeepTogether.
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
    # Insert it right after the imports or at the very beginning of the script
    content = monkey_patch + "\n" + content

    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: python compile_script.py <path_to_script>")
        sys.exit(1)

    input_script = sys.argv[1]
    if not os.path.exists(input_script):
        print(f"Error: Script not found at {input_script}")
        sys.exit(1)

    # Use the active workspace doc folder as output dir
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Reading target script: {input_script}...")
    with open(input_script, 'r', encoding='utf-8') as f:
        code_content = f.read()

    print("Applying patches...")
    patched_code = patch_code(code_content, workspace_dir)

    # Create a temporary file to run the patched script
    # We create it in the workspace so relative imports or virtual env paths resolve correctly
    temp_fd, temp_path = tempfile.mkstemp(suffix='.py', dir=workspace_dir)
    os.close(temp_fd)

    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(patched_code)

        print(f"Executing patched code using virtual environment...")
        
        # Path to virtual env python
        python_exe = os.path.join(workspace_dir, ".venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            # Fallback to system python if venv python isn't found
            python_exe = sys.executable

        # Run the temporary script
        result = subprocess.run([python_exe, temp_path], capture_output=True, text=True)

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
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    main()
