"""
Terminal command execution utilities for AI Code Helper.

Basit ve doğrudan terminal komut çalıştırma işlevselliği.
"""
import subprocess
import os
import logging
import shlex
import sys
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logger = logging.getLogger("ai_code_helper.terminal_commands")

def execute_command(command: str, cwd: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
    """
    Execute a terminal command and return the result.
    
    Args:
        command: The command to execute
        cwd: The current working directory for the command (optional)
        timeout: Timeout in seconds (default: 60)
        
    Returns:
        Dictionary with command execution results
        {
            "status": "success" or "error",
            "stdout": stdout output (if success),
            "stderr": stderr output (if error),
            "exit_code": command exit code,
            "message": success or error message
        }
    """
    if not command:
        return {
            "status": "error",
            "stderr": "No command provided",
            "exit_code": 1,
            "message": "No command provided"
        }
    
    try:
        logger.info(f"Executing command: {command}")
        
        # Windows'ta PowerShell kullanarak daha basit yaklaşım
        if sys.platform == "win32":
            # PowerShell komutunu oluşturma
            current_dir = cwd if cwd else os.getcwd()
            ps_command = f"powershell.exe -Command \"cd '{current_dir}'; {command}\""
            
            # Komutu çalıştırma
            result = subprocess.run(
                ps_command, 
                capture_output=True, 
                text=True, 
                shell=True,
                timeout=timeout
            )
        else:
            # Windows olmayan sistemlerde standart çalıştırma
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                cwd=cwd,
                timeout=timeout
            )
        
        # Sonuçları işleme
        if result.returncode == 0:
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "message": "Command executed successfully"
            }
        else:
            return {
                "status": "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "message": f"Command failed with exit code {result.returncode}: {result.stderr}"
            }
            
    except subprocess.TimeoutExpired as e:
        return {
            "status": "error",
            "stderr": str(e),
            "exit_code": 124,  # Common timeout exit code
            "message": f"Command execution timed out after {timeout} seconds"
        }
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {
            "status": "error",
            "stderr": str(e),
            "exit_code": 1,
            "message": f"Error executing command: {e}"
        }

def is_safe_command(command: str) -> bool:
    """
    Check if a command is safe to execute.
    
    Args:
        command: The command to check
        
    Returns:
        True if the command is considered safe, False otherwise
    """
    # Split the command to get the base command
    try:
        cmd_parts = shlex.split(command)
        base_cmd = cmd_parts[0].lower() if cmd_parts else ""
    except Exception:
        # If we can't parse it, assume it's not safe
        return False
    
    # List of potentially dangerous commands
    dangerous_commands = [
        "rm", "rmdir", "del", "format", "shutdown", "reboot",
        "sudo", "su", "chown", "chmod", "mkfs", "dd",
        "wget", "curl", ">", ">>", "|"  # Commands that could download or redirect output
    ]
    
    # Check for dangerous commands or patterns
    for cmd in dangerous_commands:
        if cmd in command.lower():
            logger.warning(f"Potentially dangerous command detected: {command}")
            return False
    
    return True

def suggest_safe_alternatives(command: str) -> List[str]:
    """
    Suggest safer alternatives for potentially dangerous commands.
    
    Args:
        command: The original command
        
    Returns:
        List of suggested safer alternatives
    """
    suggestions = []
    
    # Map of dangerous commands to safer alternatives
    alternatives = {
        "rm": ["Use file explorer to delete files", "Use a script with confirmation prompts"],
        "rmdir": ["Use file explorer to delete directories", "Create a backup before deleting"],
        "sudo": ["Run the command without elevated privileges if possible"],
        "format": ["Use a GUI disk management tool instead"],
        "dd": ["Use a specialized backup/restore tool with safeguards"]
    }
    
    # Check for matches and add suggestions
    for cmd, alts in alternatives.items():
        if cmd in command.lower():
            suggestions.extend(alts)
    
    if not suggestions:
        suggestions.append("Consider reviewing the command manually before execution")
        
    return suggestions
