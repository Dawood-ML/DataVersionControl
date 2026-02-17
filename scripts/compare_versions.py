import pandas as pd
import subprocess
import tempfile
import os
def get_dvc_file_for_commit(commit_hash, dvc_file):
    """
    Get data file for specific Git commit.
    
    WHAT: Checkout old .dvc file, pull corresponding data
    WHY: Compare data across versions
    WHEN: Need historical data
    WHEN NOT: Current version only
    ALTERNATIVE: Manual git checkout
    """
    # Checkout .dvc file from commit
    subprocess.run(['git', 'checkout', commit_hash, dvc_file], 
                   capture_output=True, check=True)
    
    # Get data for that .dvc file
    subprocess.run(['uv', 'run', 'dvc', 'checkout', dvc_file], 
                   capture_output=True, check=True)

def compare_datasets(v1_path, v2_path):
    """
    Compare two dataset versions.
    
    WHAT: Load both versions and show differences
    WHY: Understand data changes
    WHEN: Investigating version differences
    WHEN NOT: N/A
    ALTERNATIVE: Manual comparison
    """
    df_v1 = pd.read_csv(v1_path)
    df_v2 = pd.read_csv(v2_path)
    
    print("="*60)
    print("DATASET VERSION COMPARISON")
    print("="*60)
    
    print(f"\n📊 V1 (older):")
    print(f"   Records: {len(df_v1):,}")
    print(f"   Columns: {len(df_v1.columns)}")
    print(f"   Churn rate: {df_v1['churn'].mean():.1%}")
    print(f"   Age range: {df_v1['age'].min()}-{df_v1['age'].max()}")
    
    print(f"\n📊 V2 (newer):")
    print(f"   Records: {len(df_v2):,}")
    print(f"   Columns: {len(df_v2.columns)}")
    print(f"   Churn rate: {df_v2['churn'].mean():.1%}")
    print(f"   Age range: {df_v2['age'].min()}-{df_v2['age'].max()}")
    
    print(f"\n📈 Changes:")
    print(f"   Records: {len(df_v2) - len(df_v1):+,}")
    print(f"   Churn rate: {(df_v2['churn'].mean() - df_v1['churn'].mean()) * 100:+.1f} percentage points")
    
    # Check for column changes
    v1_cols = set(df_v1.columns)
    v2_cols = set(df_v2.columns)
    
    if v1_cols == v2_cols:
        print(f"   Schema: Unchanged ✅")
    else:
        added = v2_cols - v1_cols
        removed = v1_cols - v2_cols
        if added:
            print(f"   Columns added: {added}")
        if removed:
            print(f"   Columns removed: {removed}")
    
    print("="*60)

if __name__ == "__main__":
    print("\n🔄 Fetching v1 data...")
    
    # Get v1 (second-to-last commit)
    get_dvc_file_for_commit('HEAD~1', 'data/raw/customers.csv.dvc')
    
    # Copy v1 to temp location
    import shutil
    shutil.copy('data/raw/customers.csv', '/tmp/customers_v1.csv')
    
    print("🔄 Fetching v2 data...")
    
    # Get v2 (latest)
    get_dvc_file_for_commit('HEAD', 'data/raw/customers.csv.dvc')
    
    # Compare
    compare_datasets('/tmp/customers_v1.csv', 'data/raw/customers.csv')
    
    # Cleanup
    os.remove('/tmp/customers_v1.csv')