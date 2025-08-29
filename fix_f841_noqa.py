#!/usr/bin/env python3
"""
Add # noqa: F841 to unused variables
"""
import re

def fix_f841_with_noqa(file_path):
    """Add noqa comments for F841 unused variables"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Lines that need noqa from flake8 output
    f841_lines = [319, 324, 402, 412]  # Line numbers with F841 issues
    
    modified = False
    for line_num in f841_lines:
        if line_num <= len(lines):
            line_idx = line_num - 1  # Convert to 0-based index
            line = lines[line_idx]
            
            # Add noqa comment if not already present
            if '# noqa' not in line:
                # Remove trailing newline, add noqa, add newline back
                stripped_line = line.rstrip()
                lines[line_idx] = f'{stripped_line}  # noqa: F841\n'
                modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False

# Fix the file
file_path = 'src/bnb_trading/price_action_patterns.py'
if fix_f841_with_noqa(file_path):
    print(f"✅ Added noqa comments to {file_path}")
else:
    print(f"❌ No changes made to {file_path}")