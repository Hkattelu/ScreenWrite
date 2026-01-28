"""
Interactive onboarding script to finalize environment setup.
"""

import sys
from screenwrite.utils.dependency_checker import DependencyChecker
from screenwrite.utils.env_manager import EnvManager

def main():
    print("========================================")
    print("   screenwrite Onboarding Wizard")
    print("========================================\n")

    checker = DependencyChecker()
    env_mgr = EnvManager()

    # 1. Check Dependencies
    print("[1/2] Checking system dependencies...")
    missing = checker.get_missing_report()
    
    if not missing:
        print("âœ… All system dependencies found.\n")
    else:
        print("âš  Some dependencies are missing:")
        for name, link in missing:
            print(f"  - {name}: Download at {link}")
        print("\nPlease install these for full functionality.\n")

    # 2. Configure .env
    print("[2/2] Configuring environment variables...")
    
    # Root .env
    env_mgr.ensure_env_exists(".env.example", ".env")
    
    # Frontend .env
    frontend_env_mgr = EnvManager(base_path="webapp/frontend")
    frontend_env_mgr.ensure_env_exists(".env.example", ".env")

    # Check for Gemini Key
    gemini_key = ""
    # Try to read existing key
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip()

    if not gemini_key or gemini_key == "your_api_key_here":
        print("\nYour Gemini API Key is missing.")
        key = env_mgr.prompt_for_key()
        if key:
            env_mgr.update_env_key(".env", "GEMINI_API_KEY", key)
            print("âœ… .env updated successfully.")
        else:
            print("â„¹ï¸  Skipped API key configuration. You can add it later to .env.")
    else:
        print("âœ… Gemini API key already configured.")

    print("\n========================================")
    print("   Setup Complete! Happy Screenwriting.")
    print("========================================\n")

if __name__ == "__main__":
    import os
    main()
