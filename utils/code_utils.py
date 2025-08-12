"""
Utility functions for code analysis and generation.
"""
import re
import os
from typing import Dict, List, Any, Optional, Tuple

def detect_language(code: str) -> Optional[str]:
    """
    Detect the programming language of the code.
    
    Args:
        code: The source code to analyze
        
    Returns:
        The detected language or None if unable to detect
    """
    # A simple language detection based on file extensions and patterns
    language_patterns = {
        "python": [r'^\s*import\s+', r'^\s*from\s+.+\s+import', r'^\s*def\s+', r'^\s*class\s+'],
        "javascript": [r'^\s*const\s+', r'^\s*let\s+', r'^\s*function\s+', r'^\s*import\s+.+\s+from'],
        "typescript": [r'^\s*interface\s+', r'^\s*type\s+', r':\s*[A-Za-z]+'],
        "java": [r'^\s*public\s+class', r'^\s*private\s+', r'^\s*protected\s+', r'^\s*import\s+java\.'],
        "c": [r'#include\s+<', r'^\s*int\s+main\s*\('],
        "cpp": [r'#include\s+<', r'std::', r'namespace\s+', r'template\s*<'],
        "csharp": [r'^\s*using\s+System', r'namespace\s+', r'public\s+class'],
        "php": [r'<\?php', r'\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*'],
        "go": [r'package\s+', r'func\s+', r'import\s+\('],
        "ruby": [r'^\s*require\s+', r'^\s*class\s+', r'^\s*def\s+', r'^\s*end'],
        "rust": [r'fn\s+', r'let\s+mut', r'struct\s+', r'impl\s+'],
        "kotlin": [r'fun\s+', r'val\s+', r'var\s+', r'class\s+'],
        "swift": [r'func\s+', r'var\s+', r'let\s+', r'class\s+'],
        "html": [r'<!DOCTYPE\s+html>', r'<html', r'<head', r'<body'],
        "css": [r'^\s*\.[a-zA-Z]', r'^\s*#[a-zA-Z]', r'{\s*[a-zA-Z-]+\s*:'],
        "sql": [r'^\s*SELECT\s+', r'^\s*INSERT\s+INTO', r'^\s*UPDATE\s+', r'^\s*CREATE\s+TABLE'],
    }
    
    for lang, patterns in language_patterns.items():
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                return lang
    
    return None

def extract_imports(code: str, language: str) -> List[str]:
    """
    Extract import statements from the code based on the language.
    
    Args:
        code: The source code to analyze
        language: The programming language of the code
        
    Returns:
        A list of imported modules or packages
    """
    imports = []
    
    if language == "python":
        # Match Python imports
        import_patterns = [
            r'^\s*import\s+([\w\.]+)',
            r'^\s*from\s+([\w\.]+)\s+import'
        ]
        for pattern in import_patterns:
            imports.extend(re.findall(pattern, code, re.MULTILINE))
    
    elif language in ["javascript", "typescript"]:
        # Match JavaScript/TypeScript imports
        import_patterns = [
            r'^\s*import\s+.*\s+from\s+[\'"](.+)[\'"]',
            r'^\s*const\s+\w+\s+=\s+require\([\'"](.+)[\'"]\)'
        ]
        for pattern in import_patterns:
            imports.extend(re.findall(pattern, code, re.MULTILINE))
    
    elif language in ["java", "kotlin"]:
        # Match Java/Kotlin imports
        imports = re.findall(r'^\s*import\s+([\w\.]+);', code, re.MULTILINE)
    
    elif language in ["c", "cpp"]:
        # Match C/C++ includes
        imports = re.findall(r'^\s*#include\s+[<"]([\w\.\/]+)[>"]', code, re.MULTILINE)
    
    return imports

def extract_code_metadata(code: str) -> Dict[str, Any]:
    """
    Extract metadata from code to help with coding assistance.
    
    Args:
        code: The source code to analyze
        
    Returns:
        A dictionary containing code metadata
    """
    language = detect_language(code)
    
    metadata = {
        "language": language,
        "imports": [],
        "frameworks": [],
        "code_length": len(code),
        "line_count": len(code.split("\n")),
    }
    
    if language:
        metadata["imports"] = extract_imports(code, language)
        # Detect frameworks based on imports (simplified)
        framework_patterns = {
            "django": ["django"],
            "flask": ["flask"],
            "react": ["react"],
            "angular": ["@angular"],
            "vue": ["vue"],
            "express": ["express"],
            "spring": ["org.springframework"],
        }
        
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if any(pattern.lower() in imp.lower() for imp in metadata["imports"]):
                    metadata["frameworks"].append(framework)
                    break
    
    return metadata

def save_code_to_file(code: str, language: str = None, file_path: str = None, description: str = None) -> Dict[str, Any]:
    """
    Save generated code to a file with appropriate extension.
    
    Args:
        code: The code to save
        language: The programming language of the code (optional, will be detected if not provided)
        file_path: Specific file path to save to (optional)
        description: Description of the code for generating a filename (optional)
        
    Returns:
        Dictionary with status and file path information
    """
    if not language:
        language = detect_language(code)
        if not language:
            language = "txt"  # Default to text if language cannot be determined
    
    # Define file extension mapping
    extension_map = {
        "python": "py",
        "javascript": "js",
        "typescript": "ts",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "csharp": "cs",
        "php": "php",
        "go": "go",
        "ruby": "rb",
        "rust": "rs",
        "kotlin": "kt",
        "swift": "swift",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "txt": "txt"
    }
    
    # Get the appropriate extension
    extension = extension_map.get(language, "txt")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Always use a timestamp to ensure uniqueness
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if file_path:
        # If file_path was specified, we'll still make it unique with a timestamp
        base_path, ext = os.path.splitext(file_path)
        if not ext:  # If no extension provided
            ext = f".{extension}"
        # Create a unique name by adding timestamp
        full_path = f"{base_path}_{timestamp}{ext}"
    else:
        # Generate filename based on description or default
        if description:
            # Generate filename from description (remove special chars, lowercase, replace spaces with _)
            base_filename = re.sub(r'[^\w\s]', '', description.lower())[:30]
            base_filename = base_filename.replace(' ', '_')
            filename = f"{base_filename}_{timestamp}"
        else:
            # Generate a truly unique name instead of always using "generated_code"
            filename = f"code_{timestamp}"
        
        full_path = os.path.join(data_dir, f"{filename}.{extension}")
    
    try:
        # Make sure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
        
        # Write code to file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return {
            "status": "success",
            "file_path": full_path,
            "language": language,
            "extension": extension
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
