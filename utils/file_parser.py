from dataclasses import dataclass
import os
@dataclass
class CodeSnippet:
    file_path: str
    start_line: int
    end_line: int
    content: str
    snippet_type: str 

class FileParser:
    def __init__(self, project_root: str, extensions: list[str] = None):
        self.project_root=project_root
        if extensions is None:  # ✅ проверка
            self.extensions = [".py", ".c", ".h", ".js", ".ts"]  # значения по умолчанию
        else:
            self.extensions = extensions
    def scan_project(self) -> list[str]:
        skip = ["_pycache_", ".git", "node_modules", "venv"]
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in skip]
            for file in files:
                if any(file.endswith(ext) for ext in self.extensions):
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        return all_files
    def parse_file(self, file_path: str) -> list[CodeSnippet]:
        snippets = []  
        current_snippet_lines = []  
        current_start_line = 0
        current_type = "file" 
        in_snippet = False
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, start=1):
                if line.startswith(("def ", "class ", "import ", "#include ")):
                    if in_snippet and current_snippet_lines:
                        snippet = CodeSnippet(
                            file_path=file_path,
                            start_line=current_start_line,
                            end_line=line_num - 1,
                            content="".join(current_snippet_lines),
                            snippet_type=current_type
                        )
                        snippets.append(snippet)
                    
                    in_snippet = True
                    current_start_line = line_num
                    current_snippet_lines = [line]
                    
                    if line.startswith("def "):
                        current_type = "function"
                    elif line.startswith("class "):
                        current_type = "class"
                    elif line.startswith("import "):
                        current_type = "import"
                    elif line.startswith("#include"):
                        current_type = "include"
                elif in_snippet:
                    current_snippet_lines.append(line)
            
            if in_snippet and current_snippet_lines:
                snippet = CodeSnippet(
                    file_path=file_path,
                    start_line=current_start_line,
                    end_line=line_num,  
                    content="".join(current_snippet_lines),
                    snippet_type=current_type
                )
                snippets.append(snippet)
        
        return snippets
    def search_by_keyword(self, keyword: str, files: list[str] = None) -> list[CodeSnippet]:
        results=[]
        if files is None:
            files = self.scan_project()
        for file_path in files:
            content = self.get_file_content(file_path)
            if keyword.lower() in content.lower():
                lines=content.splitlines()
                for line_num, line in enumerate(lines, start=1):
                    if keyword.lower() in line.lower():
                        start_line = max(1, line_num - 5)
                        end_line = min(len(lines), line_num + 5)
                        context_lines = lines[start_line-1:end_line] 
                        context_text = "\n".join(context_lines)  
                        snippet = CodeSnippet(
                            file_path=file_path,
                            start_line=start_line,
                            end_line=end_line,
                            content=context_text,
                            snippet_type="match"    
                        )
                        results.append(snippet)
        return results
    def get_file_content(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
