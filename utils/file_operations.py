"""
Utility functions for file and directory operations.
"""
import os
import shutil
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def create_directory(path: str) -> Dict[str, Any]:
    """
    Create a new directory.
    
    Args:
        path: Path of the directory to create
        
    Returns:
        Dictionary with status and message
    """
    try:
        os.makedirs(path, exist_ok=True)
        return {
            "status": "success",
            "message": f"Directory created successfully: {path}"
        }
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to create directory: {str(e)}"
        }

def delete_directory(path: str) -> Dict[str, Any]:
    """
    Delete a directory and all its contents.
    
    Args:
        path: Path of the directory to delete
        
    Returns:
        Dictionary with status and message
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return {
                "status": "success",
                "message": f"Directory deleted successfully: {path}"
            }
        return {
            "status": "error",
            "message": f"Directory does not exist: {path}"
        }
    except Exception as e:
        logger.error(f"Error deleting directory {path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to delete directory: {str(e)}"
        }

def list_directory(path: str) -> Dict[str, Any]:
    """
    List contents of a directory.
    
    Args:
        path: Path of the directory to list
        
    Returns:
        Dictionary with status and directory contents
    """
    try:
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"Directory does not exist: {path}"
            }
            
        contents = os.listdir(path)
        files = []
        directories = []
        
        for item in contents:
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                files.append(item)
            elif os.path.isdir(full_path):
                directories.append(item)
                
        return {
            "status": "success",
            "files": files,
            "directories": directories
        }
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to list directory: {str(e)}"
        }

def move_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Move a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        Dictionary with status and message
    """
    try:
        if not os.path.exists(source):
            return {
                "status": "error",
                "message": f"Source file does not exist: {source}"
            }
            
        shutil.move(source, destination)
        return {
            "status": "success",
            "message": f"File moved successfully from {source} to {destination}"
        }
    except Exception as e:
        logger.error(f"Error moving file from {source} to {destination}: {e}")
        return {
            "status": "error",
            "message": f"Failed to move file: {str(e)}"
        }

def copy_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        Dictionary with status and message
    """
    try:
        if not os.path.exists(source):
            return {
                "status": "error",
                "message": f"Source file does not exist: {source}"
            }
            
        shutil.copy2(source, destination)
        return {
            "status": "success",
            "message": f"File copied successfully from {source} to {destination}"
        }
    except Exception as e:
        logger.error(f"Error copying file from {source} to {destination}: {e}")
        return {
            "status": "error",
            "message": f"Failed to copy file: {str(e)}"
        } 