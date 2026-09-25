import os
import subprocess
from pathlib import Path
import environ

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

def restore_database(backup_file):
    """Restore PostgreSQL database from backup"""
    
    backup_path = BASE_DIR / backup_file
    if not backup_path.exists():
        print(f"✗ Error: Backup file {backup_path} does not exist.")
        return

    env_vars = os.environ.copy()
    env_vars['PGPASSWORD'] = env('DB_PASSWORD')
    
    cmd = [
        'psql',
        '-h', env('DB_HOST', default='localhost'),
        '-U', env('DB_USER'),
        '-d', env('DB_NAME'),
        '-f', str(backup_path)
    ]
    
    print(f"Restoring database from {backup_path}...")
    result = subprocess.run(cmd, env=env_vars, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Restore successful from: {backup_path}")
    else:
        print(f"✗ Restore failed: {result.stderr}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        restore_database(sys.argv[1])
    else:
        print("Usage: python scripts/restore_database.py <backup_file_name>")