#!/usr/bin/env python3
"""
Update all script imports to use backend.agents path
"""

import os
import re
from pathlib import Path

# Define the root directory
root_dir = Path(__file__).parent.parent

# Scripts to update
scripts_to_update = [
    'scripts/data_ingestion/ingest_simple.py',
    'scripts/data_ingestion/ingest_direct_qdrant.py',
    'scripts/setup/setup_qdrant_local.py',
    'scripts/tests/test_gemini_setup.py',
]

# Path setup code to add
path_setup = """
# Add backend directory to path
backend_path = Path(__file__).parent.parent.parent / 'backend'
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
"""

def update_script(script_path):
    """Update imports in a script file"""
    full_path = root_dir / script_path
    
    if not full_path.exists():
        print(f"⚠️  Skipping {script_path} - file not found")
        return
    
    print(f"📝 Updating {script_path}...")
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Update sys.path.append to new backend path
    content = re.sub(
        r"sys\.path\.append\(.*?\)",
        "# Path added below",
        content
    )
    
    # Replace old path setup with new one
    if 'from pathlib import Path' in content and 'backend_path' not in content:
        # Find the import section
        lines = content.split('\n')
        new_lines = []
        import_section_done = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add backend path after imports but before other code
            if not import_section_done and line.strip() and not line.startswith('import') and not line.startswith('from') and not line.startswith('#'):
                if 'sys.path' not in '\n'.join(lines[max(0, i-5):i]):
                    new_lines.insert(-1, path_setup)
                    import_section_done = True
        
        content = '\n'.join(new_lines)
    
    # Update config import
    content = content.replace('from config import Config', 'from core.config import Config')
    
    # Write back
    with open(full_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {script_path}")

if __name__ == '__main__':
    print("="*60)
    print("🔧 Updating Script Imports")
    print("="*60)
    print()
    
    for script in scripts_to_update:
        update_script(script)
    
    print()
    print("="*60)
    print("✅ All scripts updated!")
    print("="*60)
