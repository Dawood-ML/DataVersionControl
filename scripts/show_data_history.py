"""
Show data version history.

WHAT: Display all versions of a dataset
WHY: Track data evolution over time
WHEN: Auditing data changes
WHEN NOT: Single version only
ALTERNATIVE: Manual git log inspection
"""

import subprocess
import json

def get_data_versions(dvc_file):
    """
    Get all versions of a DVC-tracked file.
    
    WHAT: Parse Git history for .dvc file changes
    WHY: See all data versions
    WHEN: Understanding data evolution
    WHEN NOT: N/A
    ALTERNATIVE: git log --follow
    """
    # Get git log for .dvc file
    cmd = [
        'git', 'log',
        '--pretty=format:%H|%ai|%s',  # hash|date|message
        '--follow',  # Follow file renames
        dvc_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    versions = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        commit_hash, date, message = line.split('|', 2)
        
        # Get .dvc file content at this commit
        dvc_content = subprocess.run(
            ['git', 'show', f'{commit_hash}:{dvc_file}'],
            capture_output=True, text=True, check=True
        ).stdout
        
        # Parse MD5 and size from .dvc file
        import yaml
        dvc_data = yaml.safe_load(dvc_content)
        md5 = dvc_data['outs'][0]['md5']
        size = dvc_data['outs'][0]['size']
        
        versions.append({
            'commit': commit_hash[:8],
            'date': date.split()[0],  # Just date, not time
            'message': message,
            'md5': md5[:16] + '...',  # Truncate for display
            'size_mb': size / (1024 * 1024)
        })
    
    return versions

def print_version_history(versions):
    """
    Print version history table.
    
    WHAT: Format and display versions
    WHY: Human-readable history
    WHEN: After getting versions
    WHEN NOT: N/A
    ALTERNATIVE: JSON output
    """
    print("\n" + "="*80)
    print("DATA VERSION HISTORY: data/raw/customers.csv")
    print("="*80)
    
    # Header
    print(f"\n{'Ver':<4} {'Commit':<10} {'Date':<12} {'Size (MB)':<12} {'MD5 (truncated)'}")
    print("-" * 80)
    
    # Versions (reverse order - newest first)
    for idx, v in enumerate(reversed(versions), 1):
        print(f"{idx:<4} {v['commit']:<10} {v['date']:<12} {v['size_mb']:<12.2f} {v['md5']}")
    
    print("\n" + "="*80)
    print(f"Total versions: {len(versions)}")
    print("\nTo checkout a specific version:")
    print("  git checkout <commit> data/raw/customers.csv.dvc")
    print("  uv run dvc checkout data/raw/customers.csv.dvc")
    print("="*80 + "\n")

if __name__ == "__main__":
    versions = get_data_versions('data/raw/customers.csv.dvc')
    print_version_history(versions)