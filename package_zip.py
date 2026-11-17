"""
package_zip.py
--------------
Creates a clean, portable ZIP archive of the react-travel-agent project.
Excludes bytecode caches and temporary files.
"""

import os
import zipfile


def create_project_zip(project_dir: str, zip_output_path: str):
    with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Prune cache directories
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", ".git", ".vscode")]
            for file in files:
                if file.endswith((".pyc", ".pyo", ".pyd")):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.dirname(project_dir))
                zipf.write(file_path, rel_path)
    print(f"[+] Clean ZIP archive created successfully: {zip_output_path}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    proj_dir = os.path.join(current_dir, "react-travel-agent")
    out_zip = os.path.join(current_dir, "react-travel-agent.zip")
    create_project_zip(proj_dir, out_zip)

