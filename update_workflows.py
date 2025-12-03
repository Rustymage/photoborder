#!/usr/bin/env python3
"""Update workflow files to fix paths and make Python detection flexible."""

import os
import re
from pathlib import Path

# Get the absolute path to the photoborder directory
photoborder_dir = Path(__file__).parent.absolute()

# New shell script template
new_script_template = '''for f in "$@"; do
    cd "$(dirname "$f")"
    
    # Try to find python (pyenv first, then system python3)
    if [ -f ~/.pyenv/shims/python ]; then
        PYTHON=~/.pyenv/shims/python
    elif command -v python3 2>/dev/null; then
        PYTHON=python3
    else
        PYTHON=python
    fi
    
    "$PYTHON" {photoborder_path}/main.py {args} "$f"
done
'''

# Find all workflow files
workflows_dir = photoborder_dir / "osx_services"
workflow_files = list(workflows_dir.glob("*/Contents/document.wflow"))

print(f"Found {len(workflow_files)} workflow files to update")
print(f"Photoborder path: {photoborder_dir}")

for workflow_file in workflow_files:
    print(f"\nProcessing: {workflow_file.parent.parent.name}")
    
    # Read the file
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the current command to get the arguments
    # Try to match either the old whiteborder path or the new photoborder path
    match = re.search(r'(?:~/dev/whiteborder|/Users/eric/Developer/photoborder)/main\.py\s+([^\$"]*?)\s*["\$]', content)
    if match:
        args = match.group(1).strip()
        print(f"  Arguments: {args if args else '(none)'}")
        
        # Create the new script
        new_script = new_script_template.format(
            photoborder_path=photoborder_dir,
            args=args
        )
        
        # Replace the old command - match both old and broken versions
        # This pattern matches the entire shell script block regardless of current state
        old_pattern = r'<string>for f in "\$@"; do.*?done\s*</string>'
        new_replacement = f'<string>{new_script}</string>'
        
        updated_content = re.sub(old_pattern, new_replacement, content, flags=re.DOTALL)
        
        if updated_content != content:
            # Write back the file
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("  ✓ Updated successfully")
        else:
            print("  ⚠ No changes made (pattern not found)")
    else:
        print("  ✗ Could not find command pattern")

print("\n✅ All workflows processed!")
