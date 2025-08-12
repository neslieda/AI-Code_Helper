#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Code Helper
-------------
An intelligent agent system that helps software developers write, understand, and improve code
through natural language interactions.
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional, List
import subprocess

from agents.code_agent import CodeAgent
from utils.file_operations import (
    create_directory,
    delete_directory,
    list_directory,
    move_file,
    copy_file
)
from utils.terminal_commands import execute_command, is_safe_command, suggest_safe_alternatives
# Artık OpenAI API anahtarına ihtiyacımız yok
# from utils.config import get_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_code_helper.log')
    ]
)
logger = logging.getLogger("ai_code_helper")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI Code Helper - A natural language coding assistant")
    
    # AI Code Helper arguments
    parser.add_argument("--model", type=str, default="gpt-4", help="The OpenAI model to use (e.g., gpt-4, gpt-4)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--request", type=str, help="Process a single request and exit")
    parser.add_argument("--code_file", type=str, help="File containing code to analyze")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--generate-project", type=str, help="Tam otomatik proje oluştur: Kodları yazar, bağımlılıkları kurar ve çalıştırır. Örnek: --generate-project 'LSTM modeli eğit'")
    
    # File operations subparsers
    subparsers = parser.add_subparsers(dest="command", help="File operation commands")
    
    # Create directory command
    mkdir_parser = subparsers.add_parser("mkdir", help="Create a new directory")
    mkdir_parser.add_argument("path", type=str, help="Path of the directory to create")
    
    # Delete directory command
    rmdir_parser = subparsers.add_parser("rmdir", help="Delete a directory")
    rmdir_parser.add_argument("path", type=str, help="Path of the directory to delete")
    
    # List directory command
    ls_parser = subparsers.add_parser("ls", help="List directory contents")
    ls_parser.add_argument("path", type=str, help="Path of the directory to list")
    
    # Move file command
    mv_parser = subparsers.add_parser("mv", help="Move a file")
    mv_parser.add_argument("source", type=str, help="Source file path")
    mv_parser.add_argument("destination", type=str, help="Destination file path")
    
    # Copy file command
    cp_parser = subparsers.add_parser("cp", help="Copy a file")
    cp_parser.add_argument("source", type=str, help="Source file path")
    cp_parser.add_argument("destination", type=str, help="Destination file path")
    
    # Terminal command execution - command'ı tek bir string olarak alıyoruz
    cmd_parser = subparsers.add_parser("run", help="Execute a terminal command")
    cmd_parser.add_argument("command", type=str, help="Command to execute")
    cmd_parser.add_argument("--cwd", type=str, help="Current working directory for the command")
    cmd_parser.add_argument("--timeout", type=int, default=60, help="Command timeout in seconds (default: 60)")
    
    return parser.parse_args()

def handle_file_operations(args):
    """Handle file operation commands."""
    if args.command == "mkdir":
        result = create_directory(args.path)
    elif args.command == "rmdir":
        result = delete_directory(args.path)
    elif args.command == "ls":
        result = list_directory(args.path)
    elif args.command == "mv":
        result = move_file(args.source, args.destination)
    elif args.command == "cp":
        result = copy_file(args.source, args.destination)
    elif args.command == "run":
        return handle_terminal_command(args)
    else:
        return 1
        
    if result["status"] == "success":
        if args.command == "ls":
            print("\nFiles:")
            for file in result["files"]:
                print(f"  {file}")
            print("\nDirectories:")
            for directory in result["directories"]:
                print(f"  {directory}")
        else:
            print(result["message"])
        return 0
    else:
        print(f"Error: {result['message']}")
        return 1

def setup_environment() -> bool:
    """
    Set up the environment by checking for required packages.
    
    Returns:
        True if setup was successful, False otherwise
    """
    try:
        # Check for required packages
        import openai
        from langchain_openai import ChatOpenAI
        
        # Verify OpenAI API key is set
        from utils.config import get_api_key
        api_key = get_api_key("openai")
        if not api_key:
            logger.error("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
            return False
            
        return True
    except ImportError as e:
        logger.error(f"Required package not found: {e}")
        logger.error("Please install all required packages using: pip install -r requirements.txt")
        return False

def read_code_file(file_path: str) -> Optional[str]:
    """
    Read code from a file.
    
    Args:
        file_path: Path to the code file
        
    Returns:
        The content of the file or None if the file could not be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def handle_terminal_command(args):
    """
    Handle terminal command execution.
    
    Args:
        args: Command line arguments
        
    Returns:
        0 if successful, 1 if error
    """
    if not args.command:
        print("Error: No command provided")
        return 1
    
    # Komut güvenli mi kontrol et
    if not is_safe_command(args.command):
        print(f"Error: The command '{args.command}' may be potentially dangerous and has been blocked for safety reasons.")
        
        # Öneriler
        alternatives = suggest_safe_alternatives(args.command)
        if alternatives:
            print("\nSuggestions:")
            for alt in alternatives:
                print(f"- {alt}")
                
        return 1
    
    # Komutu çalıştır
    try:
        result = execute_command(args.command, cwd=args.cwd, timeout=args.timeout)
        
        if result["status"] == "success":
            print("Command executed successfully:\n")
            print(result["stdout"])
            return 0
        else:
            print(f"Command execution failed with exit code {result['exit_code']}:\n")
            print(result["stderr"])
            return 1
            
    except Exception as e:
        logger.error(f"Error executing terminal command: {e}")
        print(f"Error executing terminal command: {e}")
        return 1

def run_interactive_mode(agent: CodeAgent):
    """
    Run the AI Code Helper in interactive mode.
    
    Args:
        agent: The CodeAgent instance to use
    """
    print("="*80)
    print(" AI Code Helper - Interactive Mode ")
    print(" Type 'exit', 'quit', or 'q' to end the session ")
    print(" Use !cmd, !run, or !terminal followed by a command to execute terminal commands ")
    print("="*80)
    
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Exiting AI Code Helper. Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            print("\nProcessing your request...\n")
            result = agent.process_request(user_input)
            
            if result["status"] == "success":
                print(result["response"])
            else:
                print(f"Error: {result.get('error_message', 'Unknown error')}")
                if "additional_info" in result:
                    print(result["additional_info"])
                
        except KeyboardInterrupt:
            print("\nExiting AI Code Helper. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"An error occurred: {e}")

def process_single_request(agent: CodeAgent, request: str, code_file: Optional[str] = None):
    """
    Process a single request and exit.
    
    Args:
        agent: The CodeAgent instance to use
        request: The user request to process
        code_file: Optional path to a code file to include in the context
    """
    if code_file:
        code = read_code_file(code_file)
        if code:
            request = f"The following code:\n\n```\n{code}\n```\n\n{request}"
    
    result = agent.process_request(request)
    
    if result["status"] == "success":
        print(result["response"])
        return 0
    else:
        print(f"Error: {result.get('error_message', 'Unknown error')}")
        return 1

def generate_full_project(agent: CodeAgent, project_description: str):
    """
    Tam otomatik bir şekilde proje oluştur, bağımlılıkları kur ve çalıştır.
    
    Args:
        agent: The CodeAgent instance to use
        project_description: Proje açıklaması
        
    Returns:
        0 if successful, 1 if error
    """
    print(f"\n===== TAM OTOMATİK PROJE OLUŞTURMA =====\n")
    print(f"Proje Açıklaması: {project_description}")
    print("\nProje oluşturuluyor... Bu işlem birkaç dakika sürebilir.\n")
    
    # Projeyi oluştur
    result = agent.generate_project(project_description)
    
    if result["status"] == "success":
        print(f"\n✅ PROJE BAŞARIYLA OLUŞTURULDU!")
        print(f"\nProje Dizini: {result['project_dir']}")
        
        print("\n=== OLUŞTURULAN DOSYALAR ===\n")
        for file_path in result["created_files"]:
            print(f"📄 {os.path.basename(file_path)}")
        
        if result["installation_results"]:
            print("\n=== KURULUM SONUÇLARI ===\n")
            for cmd_result in result["installation_results"]:
                status = "✅" if cmd_result["success"] else "❌"
                print(f"{status} {cmd_result['command']}")
        
        if result["execution_results"]:
            print("\n=== ÇALIŞTIRMA SONUÇLARI ===\n")
            for cmd_result in result["execution_results"]:
                status = "✅" if cmd_result["success"] else "❌"
                print(f"{status} {cmd_result['command']}")
                print("\nÇıktı:")
                print(cmd_result["output"])
        
        return 0
    else:
        print(f"\n❌ PROJE OLUŞTURULURKEN HATA: {result.get('error_message', 'Bilinmeyen hata')}")
        return 1

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle file operations and terminal commands if specified
    if args.command:
        return handle_file_operations(args)
    
    # Check environment setup
    if not setup_environment():
        return 1
    
    try:
        # Initialize the Code Agent
        agent = CodeAgent(model_name=args.model)
        
        # Run in the appropriate mode
        if hasattr(args, 'generate_project') and args.generate_project:
            # Tam otomatik proje oluştur
            result = agent.generate_full_project_workflow(args.generate_project)
            print(result["message"])
            print("\n--- pip install çıktısı ---\n")
            print(result["pip_stdout"])
            if result["pip_stderr"]:
                print("\n[Hata]:", result["pip_stderr"])
            print("\n--- python model.py çıktısı ---\n")
            print(result["run_stdout"])
            if result["run_stderr"]:
                print("\n[Hata]:", result["run_stderr"])
            return 0
        elif args.interactive:
            run_interactive_mode(agent)
            return 0
        elif args.request:
            return process_single_request(agent, args.request, args.code_file)
        else:
            print("Please specify --interactive, --request, --generate-project, or a file operation command. "
                  "Use --help for more information.")
            return 1
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"An error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

