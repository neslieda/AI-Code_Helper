"""
Code Agent implementation using LangChain with OpenAI API.
"""
from typing import Dict, List, Any, Optional, Union
import logging
import os
import sys
import re
import subprocess
import time
import json
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from utils.config import get_api_key, get_model_config
from utils.code_utils import extract_code_metadata, save_code_to_file
from utils.terminal_commands import execute_command, is_safe_command, suggest_safe_alternatives
from utils.file_operations import create_directory, list_directory
from prompts.code_prompts import (
    CODE_GENERATION_PROMPT, 
    CODE_EXPLANATION_PROMPT,
    CODE_REVIEW_PROMPT,
    CODE_REFACTORING_PROMPT,
    BUG_FIXING_PROMPT,
    CODE_COMPLETION_PROMPT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_code_helper.code_agent")

# Load environment variables
load_dotenv()

class CodeAgent:
    """Agent for code-related tasks using LangChain with OpenAI API."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """
        Initialize the Code Agent.
        
        Args:
            model_name: Name of the language model to use
        """
        # Store the model name
        self.model_name = model_name
        
        # Get OpenAI API key
        self.api_key = get_api_key("openai")
        
        if not self.api_key:
            logger.error("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
            raise ValueError("OpenAI API key not found")
        
        # Initialize language model
        self._initialize_model()
        
        # Create system message
        self.system_message = """
        You are an AI Code Helper, an expert in software development with deep knowledge of programming languages,
        frameworks, and best practices. Your goal is to assist software developers with writing, understanding,
        and improving code through natural language interactions.
        
        You can:
        1. Generate code based on descriptions
        2. Explain existing code
        3. Review code and provide feedback
        4. Refactor code to improve quality
        5. Fix bugs in code
        6. Complete partial code snippets
        7. Analyze code to extract metadata
        8. Execute terminal commands to help with development tasks
        
        Respond in a helpful, clear, and concise manner.
        """
    
    def _initialize_model(self):
        """Initialize the OpenAI model."""
        try:
            logger.info(f"Initializing {self.model_name} model from OpenAI API...")
            
            # Initialize the LangChain wrapper for OpenAI
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                openai_api_key=self.api_key
            )
            
            logger.info(f"Successfully initialized {self.model_name} model")
            
        except Exception as e:
            logger.error(f"Error initializing OpenAI model: {e}")
            raise
    
    def process_request(self, user_request: str) -> Dict[str, Any]:
        """
        Process a user request.
        
        Args:
            user_request: Natural language request from the user
            
        Returns:
            Response from the agent
        """
        try:
            save_file_info = None
            
            # Check if this is a terminal command request
            if user_request.startswith("!cmd") or user_request.startswith("!run") or user_request.startswith("!terminal"):
                # Strip the command prefix and execute the terminal command
                command = user_request.split(" ", 1)[1] if " " in user_request else ""
                return self._execute_terminal_command(command)
            
            # Check if this is a library installation request
            if any(keyword in user_request.lower() for keyword in ["kütüphane", "library", "kur", "install", "yükle", "gerekli"]):
                return self._install_required_libraries(user_request)
                
            # Determine the type of request
            if "generate code" in user_request.lower() or "create code" in user_request.lower():
                # Extract language from request
                language = "python"  # Default
                for lang in ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust"]:
                    if lang in user_request.lower():
                        language = lang
                        break
                
                result = self._generate_code(
                    language=language,
                    task_description=user_request,
                    additional_context=""
                )
                
                # Save generated code to file
                # Extract code blocks from the result
                code_blocks = re.findall(r'```(?:\w+)?\s*\n([\s\S]*?)\n```', result)
                if code_blocks:
                    # Use the first code block (main code) for saving
                    code_to_save = code_blocks[0].strip()
                    # Create a unique timestamp
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Extract a description for the filename (up to 30 chars)
                    description = user_request[:100].replace("\n", " ")
                    # Create a specific unique file path
                    file_name = f"generated_code_{timestamp}.py"
                    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                    unique_file_path = os.path.join(data_dir, file_name)
                    
                    save_file_info = save_code_to_file(
                        code=code_to_save,
                        language=language,
                        file_path=unique_file_path
                    )
                
            elif "explain" in user_request.lower() and "code" in user_request.lower():
                # Extract code and language
                code_start = user_request.find("```")
                if code_start != -1:
                    code_end = user_request.find("```", code_start + 3)
                    if code_end != -1:
                        code = user_request[code_start + 3:code_end].strip()
                        language = self._detect_language_from_request(user_request) or "python"
                        result = self._explain_code(code, language)
                    else:
                        result = "Please provide code within triple backticks (```) for explanation."
                else:
                    result = "Please provide code within triple backticks (```) for explanation."
                
            elif "review" in user_request.lower() and "code" in user_request.lower():
                # Similar to explain, extract code and language
                code_start = user_request.find("```")
                if code_start != -1:
                    code_end = user_request.find("```", code_start + 3)
                    if code_end != -1:
                        code = user_request[code_start + 3:code_end].strip()
                        language = self._detect_language_from_request(user_request) or "python"
                        result = self._review_code(code, language)
                    else:
                        result = "Please provide code within triple backticks (```) for review."
                else:
                    result = "Please provide code within triple backticks (```) for review."
                
            elif "refactor" in user_request.lower():
                # Extract code, language, and refactoring goals
                code_start = user_request.find("```")
                if code_start != -1:
                    code_end = user_request.find("```", code_start + 3)
                    if code_end != -1:
                        code = user_request[code_start + 3:code_end].strip()
                        language = self._detect_language_from_request(user_request) or "python"
                        
                        # Simple extraction of refactoring goals
                        refactoring_part = user_request[code_end + 3:].strip()
                        if not refactoring_part:
                            refactoring_part = "Improve code quality, readability, and maintainability."
                            
                        result = self._refactor_code(code, language, refactoring_part)
                        
                        # Save refactored code
                        code_blocks = re.findall(r'```(?:\w+)?\s*\n([\s\S]*?)\n```', result)
                        if code_blocks:
                            code_to_save = code_blocks[0].strip()
                            # Create a unique timestamp
                            import datetime
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            # Create a specific unique file path
                            file_name = f"refactored_code_{timestamp}.{extension_map.get(language, 'txt')}"
                            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                            unique_file_path = os.path.join(data_dir, file_name)
                            
                            save_file_info = save_code_to_file(
                                code=code_to_save,
                                language=language,
                                file_path=unique_file_path
                            )
                    else:
                        result = "Please provide code within triple backticks (```) for refactoring."
                else:
                    result = "Please provide code within triple backticks (```) for refactoring."
                
            elif "fix" in user_request.lower() and ("bug" in user_request.lower() or "error" in user_request.lower()):
                # Extract code, language, bug description, and expected behavior
                code_start = user_request.find("```")
                if code_start != -1:
                    code_end = user_request.find("```", code_start + 3)
                    if code_end != -1:
                        code = user_request[code_start + 3:code_end].strip()
                        language = self._detect_language_from_request(user_request) or "python"
                        
                        # Simple extraction of bug description
                        bug_part = user_request[code_end + 3:].strip()
                        if not bug_part:
                            bug_part = "Fix the bug in the code."
                            
                        result = self._fix_bug(code, language, bug_part, "The code should work correctly.")
                        
                        # Save fixed code
                        code_blocks = re.findall(r'```(?:\w+)?\s*\n([\s\S]*?)\n```', result)
                        if code_blocks:
                            code_to_save = code_blocks[0].strip()
                            # Create a unique timestamp
                            import datetime
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            # Create a specific unique file path
                            file_name = f"fixed_code_{timestamp}.{extension_map.get(language, 'txt')}"
                            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                            unique_file_path = os.path.join(data_dir, file_name)
                            
                            save_file_info = save_code_to_file(
                                code=code_to_save,
                                language=language,
                                file_path=unique_file_path
                            )
                    else:
                        result = "Please provide code within triple backticks (```) for bug fixing."
                else:
                    result = "Please provide code within triple backticks (```) for bug fixing."
                
            elif "complete" in user_request.lower() or "finish" in user_request.lower():
                # Extract code snippet, language, and completion instructions
                code_start = user_request.find("```")
                if code_start != -1:
                    code_end = user_request.find("```", code_start + 3)
                    if code_end != -1:
                        code = user_request[code_start + 3:code_end].strip()
                        language = self._detect_language_from_request(user_request) or "python"
                        
                        # Simple extraction of completion instructions
                        completion_part = user_request[code_end + 3:].strip()
                        if not completion_part:
                            completion_part = "Complete the code according to best practices."
                            
                        result = self._complete_code(code, language, completion_part)
                        
                        # Save completed code
                        code_blocks = re.findall(r'```(?:\w+)?\s*\n([\s\S]*?)\n```', result)
                        if code_blocks:
                            code_to_save = code_blocks[0].strip()
                            # Create a unique timestamp
                            import datetime
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            # Create a specific unique file path
                            file_name = f"completed_code_{timestamp}.{extension_map.get(language, 'txt')}"
                            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                            unique_file_path = os.path.join(data_dir, file_name)
                            
                            save_file_info = save_code_to_file(
                                code=code_to_save,
                                language=language,
                                file_path=unique_file_path
                            )
                    else:
                        result = "Please provide code within triple backticks (```) for completion."
                else:
                    result = "Please provide code within triple backticks (```) for completion."
                
            elif "analyze" in user_request.lower():
                # Extract code for analysis
                code_start = user_request.find("```")
                if code_start != -1:
                    code_end = user_request.find("```", code_start + 3)
                    if code_end != -1:
                        code = user_request[code_start + 3:code_end].strip()
                        metadata = self._analyze_code(code)
                        result = f"Code Analysis Results:\n\n"
                        result += f"Language: {metadata.get('language', 'Unknown')}\n"
                        result += f"Lines of Code: {metadata.get('line_count', 0)}\n"
                        
                        if metadata.get('imports'):
                            result += f"\nImports:\n"
                            for imp in metadata.get('imports', []):
                                result += f"- {imp}\n"
                        
                        if metadata.get('frameworks'):
                            result += f"\nFrameworks Detected:\n"
                            for framework in metadata.get('frameworks', []):
                                result += f"- {framework}\n"
                    else:
                        result = "Please provide code within triple backticks (```) for analysis."
                else:
                    result = "Please provide code within triple backticks (```) for analysis."
            
            else:
                # General code help request - use raw LLM with system message
                messages = [
                    SystemMessage(content=self.system_message),
                    HumanMessage(content=user_request)
                ]
                response = self.llm.invoke(messages)
                result = response.content
                
                # Check if there are code blocks in the response and save them
                code_blocks = re.findall(r'```(\w+)?\s*\n([\s\S]*?)\n```', result)
                if code_blocks:
                    # Take the language from the first code block if specified
                    lang = None
                    if code_blocks[0][0].strip():
                        lang = code_blocks[0][0].strip()
                    code_to_save = code_blocks[0][1].strip() if len(code_blocks[0]) > 1 else code_blocks[0][0].strip()
                    
                    # Create a unique timestamp
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Get extension for the language
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
                    ext = extension_map.get(lang, "txt")
                    
                    # Create a descriptive filename based on the first few words of the request
                    request_summary = user_request.split()[:4]
                    request_summary = "_".join([word.lower() for word in request_summary if len(word) > 2])
                    file_prefix = f"code_{request_summary}" if request_summary else "unique_code"
                    
                    # Create a specific unique file path
                    file_name = f"{file_prefix}_{timestamp}.{ext}"
                    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                    unique_file_path = os.path.join(data_dir, file_name)
                    
                    save_file_info = save_code_to_file(
                        code=code_to_save,
                        language=lang,
                        file_path=unique_file_path
                    )
            
            # Add file saving information to response if applicable
            if save_file_info and save_file_info.get("status") == "success":
                file_path = save_file_info.get("file_path", "")
                file_info = f"\n\n[Code saved to file: {file_path}]"
                result += file_info
            
            return {
                "status": "success",
                "response": result,
                "file_info": save_file_info
            }
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _detect_language_from_request(self, request: str) -> Optional[str]:
        """
        Try to detect the programming language from the user request.
        
        Args:
            request: User request text
            
        Returns:
            Detected language or None
        """
        languages = {
            "python": ["python", "py", "django", "flask", "pandas", "numpy"],
            "javascript": ["javascript", "js", "node", "express", "react", "angular", "vue"],
            "typescript": ["typescript", "ts", "angular", "react", "vue"],
            "java": ["java", "spring", "android"],
            "c#": ["c#", "csharp", ".net", "dotnet", "asp.net"],
            "c++": ["c++", "cpp"],
            "go": ["go", "golang"],
            "ruby": ["ruby", "rails"],
            "php": ["php", "laravel", "symfony"],
            "rust": ["rust", "cargo"],
            "swift": ["swift", "ios"],
            "kotlin": ["kotlin", "android"],
            "html": ["html", "web"],
            "css": ["css", "style", "stylesheet"],
            "sql": ["sql", "database", "query"]
        }
        
        request_lower = request.lower()
        
        for lang, keywords in languages.items():
            for keyword in keywords:
                if keyword in request_lower:
                    return lang
        
        return None
    
    def _generate_code(self, language: str, task_description: str, additional_context: str = "") -> str:
        """
        Generate code based on a description.
        
        Args:
            language: The programming language to generate code in
            task_description: Description of what the code should do
            additional_context: Any additional context or requirements
            
        Returns:
            Generated code with explanations
        """
        prompt = CODE_GENERATION_PROMPT.format(
            language=language,
            task_description=task_description,
            additional_context=additional_context
        )
        
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def _explain_code(self, code: str, language: str) -> str:
        """
        Explain what a piece of code does.
        
        Args:
            code: The code to explain
            language: The programming language of the code
            
        Returns:
            Explanation of the code
        """
        prompt = CODE_EXPLANATION_PROMPT.format(
            code=code,
            language=language
        )
        
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def _review_code(self, code: str, language: str) -> str:
        """
        Review code and provide feedback.
        
        Args:
            code: The code to review
            language: The programming language of the code
            
        Returns:
            Code review feedback
        """
        prompt = CODE_REVIEW_PROMPT.format(
            code=code,
            language=language
        )
        
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def _refactor_code(self, code: str, language: str, refactoring_goals: str) -> str:
        """
        Refactor code according to specified goals.
        
        Args:
            code: The code to refactor
            language: The programming language of the code
            refactoring_goals: Goals for the refactoring
            
        Returns:
            Refactored code with explanations
        """
        prompt = CODE_REFACTORING_PROMPT.format(
            code=code,
            language=language,
            refactoring_goals=refactoring_goals
        )
        
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def _fix_bug(self, code: str, language: str, bug_description: str, expected_behavior: str) -> str:
        """
        Fix a bug in code.
        
        Args:
            code: The code with the bug
            language: The programming language of the code
            bug_description: Description of the bug
            expected_behavior: The expected behavior
            
        Returns:
            Fixed code with explanation
        """
        prompt = BUG_FIXING_PROMPT.format(
            code=code,
            language=language,
            bug_description=bug_description,
            expected_behavior=expected_behavior
        )
        
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def _complete_code(self, code_snippet: str, language: str, completion_instruction: str) -> str:
        """
        Complete a code snippet according to instructions.
        
        Args:
            code_snippet: The code snippet to complete
            language: The programming language of the code
            completion_instruction: Instructions for completion
            
        Returns:
            Completed code with explanation
        """
        prompt = CODE_COMPLETION_PROMPT.format(
            code_snippet=code_snippet,
            language=language,
            completion_instruction=completion_instruction
        )
        
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code and extract metadata.
        
        Args:
            code: The code to analyze
            
        Returns:
            Metadata about the code
        """
        return extract_code_metadata(code)
        
    def generate_project(self, project_description: str) -> Dict[str, Any]:
        """
        Tam otomatik bir şekilde proje oluştur, bağımlılıkları kur ve çalıştır.
        
        Args:
            project_description: Proje açıklaması
            
        Returns:
            Proje sonucu bilgileri içeren sözlük
        """
        try:
            # Zaman damgalı bir proje dizini oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = re.sub(r'[^\w]+', '_', project_description.lower())[:30]
            project_dir = f"projects/{project_name}_{timestamp}"
            
            # Proje dizinini oluştur
            create_directory(project_dir)
            
            logger.info(f"Proje dizini oluşturuldu: {project_dir}")
            
            # 1. Adım: Proje yapısını ve dosyalarını belirle
            project_structure_prompt = f"""
            Aşağıdaki proje için gerekli dosya yapısını ve her dosyanın içeriğini oluştur.
            Özellikle dikkat et: Projenin çalışması için gerekli TÜM kütüphaneleri requirements.txt'ye ekle.
            
            Proje Açıklaması: {project_description}
            
            Yanıtını şu formatta ver:
            ```json
            {{
                "proje_açıklaması": "Projenin kısa açıklaması",
                "dosyalar": [
                    {{
                        "dosya_adı": "requirements.txt",
                        "içerik": "numpy==1.19.5\npandas==1.3.0\n..."
                    }},
                    {{
                        "dosya_adı": "main.py",
                        "içerik": "import numpy as np\n...tüm kod..."
                    }}
                ],
                "kurulum_komutları": ["pip install -r requirements.txt"],
                "çalıştırma_komutları": ["python main.py"]
            }}
            ```
            
            ÖNEMLİ:
            1. requirements.txt'ye projenin çalışması için gerekli TÜM kütüphaneleri ekle
            2. Her kütüphane için spesifik versiyon numarası belirt
            3. Kodun tamamen çalışır durumda olduğundan emin ol
            4. Örnek veya placeholder kod değil, gerçek çalışan kod olmalı
            """
            
            # Proje yapısını oluştur
            messages = [
                SystemMessage(content=self.system_message),
                HumanMessage(content=project_structure_prompt)
            ]
            response = self.llm.invoke(messages)
            
            # JSON yanıtını çıkart
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response.content)
            if not json_match:
                raise ValueError("AI yanıtından JSON yapısı çıkartılamadı")
                
            project_spec = json.loads(json_match.group(1))
            
            # 2. Adım: Dosyaları oluştur
            created_files = []
            for file_spec in project_spec["dosyalar"]:
                file_path = f"{project_dir}/{file_spec['dosya_adı']}"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_spec["içerik"])
                created_files.append(file_path)
                logger.info(f"Dosya oluşturuldu: {file_path}")
            
            # 3. Adım: Bağımlılıkları otomatik kur
            installation_results = []
            
            # Önce requirements.txt'yi kontrol et
            req_file = next((f for f in project_spec["dosyalar"] if f["dosya_adı"] == "requirements.txt"), None)
            if req_file:
                logger.info("Gerekli kütüphaneler kuruluyor...")
                pip_cmd = f"pip install -r {project_dir}/requirements.txt"
                result = execute_command(pip_cmd, cwd=project_dir, timeout=300)  # 5 dakika timeout
                installation_results.append({
                    "command": pip_cmd,
                    "success": result["status"] == "success",
                    "output": result["stdout"] if result["status"] == "success" else result["stderr"]
                })
                
                if result["status"] != "success":
                    logger.error(f"Kütüphane kurulumu başarısız: {result['stderr']}")
                    return {
                        "status": "error",
                        "error_message": f"Kütüphane kurulumu başarısız: {result['stderr']}"
                    }
            
            # Diğer kurulum komutlarını çalıştır
            for command in project_spec.get("kurulum_komutları", []):
                if command != pip_cmd:  # pip install komutunu tekrar çalıştırma
                    logger.info(f"Komut çalıştırılıyor: {command}")
                    result = execute_command(command, cwd=project_dir)
                    installation_results.append({
                        "command": command,
                        "success": result["status"] == "success",
                        "output": result["stdout"] if result["status"] == "success" else result["stderr"]
                    })
                    
                    if result["status"] != "success":
                        logger.error(f"Komut başarısız: {result['stderr']}")
                        return {
                            "status": "error",
                            "error_message": f"Komut başarısız: {result['stderr']}"
                        }
            
            # 4. Adım: Kodu çalıştır
            execution_results = []
            for command in project_spec.get("çalıştırma_komutları", []):
                logger.info(f"Kod çalıştırılıyor: {command}")
                result = execute_command(command, cwd=project_dir)
                execution_results.append({
                    "command": command,
                    "success": result["status"] == "success",
                    "output": result["stdout"] if result["status"] == "success" else result["stderr"]
                })
            
            # 5. Adım: Sonuçları döndür
            return {
                "status": "success",
                "project_dir": project_dir,
                "created_files": created_files,
                "installation_results": installation_results,
                "execution_results": execution_results,
                "project_spec": project_spec,
                "message": f"Proje başarıyla oluşturuldu ve çalıştırıldı!\n\nProje dizini: {project_dir}\n\nKurulan kütüphaneler:\n{req_file['içerik'] if req_file else 'Kütüphane kurulumu yapılmadı'}"
            }
            
        except Exception as e:
            logger.error(f"Proje oluşturulurken hata: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
            
    def execute_terminal_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Terminal komutu çalıştır ve sonucu döndür.
        
        Args:
            command: Çalıştırılacak komut
            cwd: Çalışma dizini (opsiyonel)
            
        Returns:
            Komut çalıştırma sonuçlarını içeren sözlük
        """
        return self._execute_terminal_command(command, cwd)
        
    def _execute_terminal_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a terminal command and return the result.
        
        Args:
            command: The command to execute
            cwd: Current working directory (optional)
            
        Returns:
            Dictionary with command execution results
        """
        if not command.strip():
            return {
                "status": "error",
                "error_message": "No command provided"
            }
            
        # Check if the command is safe to execute
        if not is_safe_command(command):
            safe_alternatives = suggest_safe_alternatives(command)
            alternatives_text = "\n".join([f"- {alt}" for alt in safe_alternatives])
            
            return {
                "status": "error",
                "error_message": f"The command '{command}' may be potentially dangerous and has been blocked for safety reasons.",
                "additional_info": f"Suggestions:\n{alternatives_text}"
            }
        
        # Execute the command
        try:
            result = execute_command(command, cwd=cwd)
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "response": f"Command executed successfully:\n\n```\n{result['stdout']}\n```"
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Command execution failed with exit code {result['exit_code']}:\n\n```\n{result['stderr']}\n```"
                }
                
        except Exception as e:
            logger.error(f"Error executing terminal command: {e}")
            return {
                "status": "error",
                "error_message": f"Error executing terminal command: {e}"
            }

    def generate_full_project_workflow(self, user_request: str) -> dict:
        """
        Tam otomatik proje workflow'u: prompt'a göre requirements.txt ve model.py oluşturur,
        terminalden pip install ve python model.py çalıştırır, çıktıyı döner.
        """
        import re
        import os
        from utils.code_utils import save_code_to_file
        from utils.terminal_commands import execute_command
        import datetime
        
        # 1. requirements.txt oluştur
        req_prompt = f"""Aşağıdaki istek için gerekli Python kütüphanelerini requirements.txt formatında döndür.
        SADECE kütüphane isimlerini yaz, başka hiçbir şey ekleme.
        
        ÖNEMLİ KURALLAR:
        1. Sadece kütüphane isimleri olmalı
        2. Her satırda bir kütüphane olmalı
        3. pip install, !pip install gibi komut ifadeleri KULLANMA
        4. Başka açıklama veya metin EKLEME
        5. Sadece geçerli PyPI paket adlarını yaz
        6. sklearn yerine scikit-learn kullan
        
        Örnek format:
        xgboost
        pandas
        scikit-learn
        numpy

        İstek: {user_request}"""
        req_result = self.llm.invoke([{'role': 'user', 'content': req_prompt}]).content
        
        # Extract requirements from the response
        req_blocks = re.findall(r'```(?:python)?\s*([\s\S]*?)\n```', req_result)
        if not req_blocks:
            req_blocks = re.findall(r'```\s*([\s\S]*?)\n```', req_result)
        requirements = req_blocks[0].strip() if req_blocks else req_result.strip()
        
        # Clean and validate requirements
        requirements_lines = requirements.split('\n')
        valid_requirements = []
        for line in requirements_lines:
            line = line.strip()
            # Skip empty lines and lines containing pip install
            if line and not any(cmd in line.lower() for cmd in ['pip install', '!pip', 'install']):
                # Extract just the package name if there's a version specifier
                package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                # Replace sklearn with scikit-learn
                if package == 'sklearn':
                    package = 'scikit-learn'
                valid_requirements.append(package)
        
        # Remove duplicates while preserving order
        seen = set()
        valid_requirements = [x for x in valid_requirements if not (x in seen or seen.add(x))]
        
        # Join back into a string
        requirements = '\n'.join(valid_requirements)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        req_path = os.path.join(data_dir, f"requirements_{timestamp}.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(requirements)
        
        # 2. model.py oluştur
        code_prompt = f"Sadece kod bloğu olarak, {user_request} için çalışan bir python kodu üret. Kodun başına ve sonuna açıklama ekleme. Dosya adı: model.py"
        code_result = self.llm.invoke([{'role': 'user', 'content': code_prompt}]).content
        code_blocks = re.findall(r'```python\s*([\s\S]*?)\n```', code_result)
        if not code_blocks:
            code_blocks = re.findall(r'```\s*([\s\S]*?)\n```', code_result)
        model_code = code_blocks[0].strip() if code_blocks else code_result.strip()
        model_path = os.path.join(data_dir, f"model_{timestamp}.py")
        with open(model_path, "w", encoding="utf-8") as f:
            f.write(model_code)
        
        # 3. pip install -r requirements.txt
        pip_cmd = f"pip install -r {req_path}"
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Try installing with a longer timeout
                pip_result = execute_command(pip_cmd, cwd=data_dir, timeout=300)  # 5 minutes timeout
                
                if pip_result.get("status") == "success":
                    break
                    
                # If we get here, the command failed
                if attempt < max_retries - 1:
                    logger.warning(f"Pip install attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Pip install attempt {attempt + 1} failed with error: {e}, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"All pip install attempts failed: {e}")
                    pip_result = {"status": "error", "stderr": str(e)}
        
        # If pip install failed, try installing packages one by one
        if pip_result.get("status") != "success":
            logger.info("Trying to install packages one by one...")
            requirements_list = requirements.split('\n')
            for package in requirements_list:
                package = package.strip()
                if package:
                    try:
                        single_pip_cmd = f"pip install {package}"
                        single_result = execute_command(single_pip_cmd, cwd=data_dir, timeout=180)
                        if single_result.get("status") != "success":
                            logger.error(f"Failed to install {package}: {single_result.get('stderr', '')}")
                    except Exception as e:
                        logger.error(f"Error installing {package}: {e}")
        
        # 4. python model.py
        run_cmd = f"python {model_path}"
        run_result = execute_command(run_cmd, cwd=data_dir, timeout=180)
        
        # 5. Sonuçları derle
        return {
            "status": "success",
            "requirements_path": req_path,
            "model_path": model_path,
            "pip_stdout": pip_result.get("stdout", ""),
            "pip_stderr": pip_result.get("stderr", ""),
            "run_stdout": run_result.get("stdout", ""),
            "run_stderr": run_result.get("stderr", ""),
            "message": f"requirements.txt ve model.py oluşturuldu, pip install ve python çalıştırıldı.\n\nrequirements.txt: {req_path}\nmodel.py: {model_path}"
        }

    def _install_required_libraries(self, user_request: str) -> Dict[str, Any]:
        """
        Kullanıcının isteğine göre gerekli kütüphaneleri tespit edip kurar.
        
        Args:
            user_request: Kullanıcının isteği
            
        Returns:
            Kurulum sonuçları
        """
        try:
            # 1. Gerekli kütüphaneleri tespit et
            prompt = f"""
            Aşağıdaki istek için gerekli Python kütüphanelerini tespit et ve requirements.txt formatında sadece kütüphane isimlerini döndür.
            Sadece kod bloğu içinde kütüphane isimlerini yaz, başka açıklama ekleme.
            
            İstek: {user_request}
            """
            
            response = self.llm.invoke([{'role': 'user', 'content': prompt}]).content
            
            # Kütüphane listesini çıkar
            import re
            lib_blocks = re.findall(r'```(?:python)?\s*([\s\S]*?)\n```', response)
            if not lib_blocks:
                lib_blocks = re.findall(r'```\s*([\s\S]*?)\n```', response)
            
            requirements = lib_blocks[0].strip() if lib_blocks else response.strip()
            
            # 2. requirements.txt oluştur
            import os
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            os.makedirs(data_dir, exist_ok=True)
            req_path = os.path.join(data_dir, f"requirements_{timestamp}.txt")
            
            with open(req_path, "w", encoding="utf-8") as f:
                f.write(requirements)
            
            # 3. pip install komutunu çalıştır
            from utils.terminal_commands import execute_command
            pip_cmd = f"pip install -r {req_path}"
            result = execute_command(pip_cmd, cwd=data_dir, timeout=180)
            
            # 4. Sonuçları döndür
            return {
                "status": "success",
                "requirements_path": req_path,
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "message": f"Gerekli kütüphaneler tespit edildi ve kuruldu.\n\nKurulan kütüphaneler:\n{requirements}"
            }
            
        except Exception as e:
            logger.error(f"Error installing required libraries: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
