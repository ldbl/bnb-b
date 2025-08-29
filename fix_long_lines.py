#!/usr/bin/env python3
"""
Fix E501 long lines automatically
"""
import os
import re
import subprocess
import sys

def fix_long_lines(file_path):
    """Fix common long line patterns"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        original_line = line
        
        # Skip if line is not too long
        if len(line.rstrip()) <= 100:
            continue
            
        # Pattern 1: Long f-string with multiple variables 
        # f"Long text {var1} more text {var2} end"
        if 'f"' in line and '{' in line and len(line.strip()) > 100:
            # Try to break f-strings at logical points
            if ' - ' in line or ' | ' in line or ' + ' in line:
                # Don't modify complex f-strings automatically to avoid breaking them
                continue
        
        # Pattern 2: Long comment lines - just leave them
        if line.strip().startswith('#'):
            continue
            
        # Pattern 3: Long logger.info/error/warning calls
        if 'logger.' in line and ('info(' in line or 'error(' in line or 'warning(' in line):
            # Split long logger calls
            match = re.search(r'(\s*)(logger\.\w+)\((.*)\)$', line.rstrip())
            if match:
                indent, logger_call, content = match.groups()
                if len(content) > 60:  # If content is long
                    lines[i] = f'{indent}{logger_call}(\n{indent}    {content}\n{indent})\n'
                    modified = True
        
        # Pattern 4: Long return statements with dicts
        if 'return {' in line and len(line.strip()) > 100:
            # Leave complex returns alone for now
            continue
            
        # Pattern 5: Long if conditions
        if ('if ' in line or 'elif ' in line) and ' and ' in line and len(line.strip()) > 100:
            # Break long if conditions at 'and'
            indent = len(line) - len(line.lstrip())
            parts = line.strip().split(' and ')
            if len(parts) > 1:
                new_line = f'{" " * indent}{parts[0]} and (\n'
                for j, part in enumerate(parts[1:], 1):
                    if j == len(parts) - 1:
                        new_line += f'{" " * (indent + 4)}{part}\n{" " * indent})\n'
                    else:
                        new_line += f'{" " * (indent + 4)}{part} and\n'
                lines[i] = new_line
                modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False

def main():
    print("🔧 Fixing long lines (E501)...")
    
    # Find Python files with E501 issues
    try:
        result = subprocess.run(['python3', '-m', 'flake8', '--select=E501', 'src/'], 
                              capture_output=True, text=True, timeout=30)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            files_with_issues = set()
            for line in lines:
                if ':' in line:
                    file_path = line.split(':')[0]
                    files_with_issues.add(file_path)
            
            print(f"Found {len(files_with_issues)} files with long lines")
            
            fixed_count = 0
            for file_path in files_with_issues:
                if os.path.exists(file_path):
                    if fix_long_lines(file_path):
                        print(f"✅ Fixed some issues in {file_path}")
                        fixed_count += 1
            
            print(f"🎯 Modified {fixed_count} files")
            
    except Exception as e:
        print(f"Could not run flake8: {e}")
        return
    
    # Run final check
    print("🔍 Running final check...")
    try:
        result = subprocess.run(['python3', '-m', 'flake8', 'src/', '--count', '--statistics'], 
                              capture_output=True, text=True, timeout=30)
        if result.stdout:
            print("Remaining issues:")
            print(result.stdout)
        else:
            print("✅ No issues found!")
    except Exception as e:
        print(f"Could not run final check: {e}")

if __name__ == "__main__":
    main()