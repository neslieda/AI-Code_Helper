#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basit Terminal Komut Çalıştırıcı

Bu betik terminal komutlarını çalıştırmak için basit bir arayüz sağlar.
"""

import subprocess
import sys
import os
import argparse

def run_command(command, cwd=None):
    """
    Terminal komutu çalıştır ve sonucu yazdır
    
    Args:
        command (str): Çalıştırılacak komut
        cwd (str, optional): Çalışma dizini
    """
    try:
        # Komut çalıştırma
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            cwd=cwd
        )
        
        # Çıktıları yazdır
        if result.stdout:
            print("\nÇıktı:")
            print(result.stdout)
        
        if result.stderr:
            print("\nHata:")
            print(result.stderr)
            
        print(f"\nİşlem kodu: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"Hata: {e}")
        return 1

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="Terminal Komut Çalıştırıcı")
    parser.add_argument("command", help="Çalıştırılacak komut")
    parser.add_argument("--cwd", help="Çalışma dizini (opsiyonel)")
    
    # Argümanları ayrıştır
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        parser.print_help()
        return 1
    
    # Çalışma dizinini ayarla
    cwd = args.cwd if args.cwd else None
    
    # Komutu çalıştır
    return run_command(args.command, cwd)

if __name__ == "__main__":
    sys.exit(main())
