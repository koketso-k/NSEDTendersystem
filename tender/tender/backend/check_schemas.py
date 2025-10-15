# Create check_schemas.py
# check_schemas.py - Check and fix schema issues
import re

def check_file_for_regex(file_path):
    print(f"🔍 Checking {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for regex patterns that might be causing issues
        regex_patterns = re.findall(r'regex=.*', content)
        if regex_patterns:
            print(f"❌ Found regex patterns in {file_path}:")
            for pattern in regex_patterns:
                print(f"   - {pattern}")
            return True
        else:
            print(f"✅ No regex issues found in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

# Check problematic files
files_to_check = ["schemas.py", "auth.py", "main.py"]
issues_found = []

for file in files_to_check:
    if check_file_for_regex(file):
        issues_found.append(file)

if issues_found:
    print(f"\n❌ Issues found in: {issues_found}")
    print("We need to fix these files.")
else:
    print("\n✅ No regex issues found!")