import os
import subprocess
from datetime import datetime
from pathlib import Path
import environ

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

def backup_database():
    """Create PostgreSQL database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f'restaurant_portal_{timestamp}.sql'
    
    # Set PGPASSWORD environment variable for non-interactive auth
    env_vars = os.environ.copy()
    env_vars['PGPASSWORD'] = env('DB_PASSWORD')
    
    cmd = [
        'pg_dump',
        '-h', env('DB_HOST', default='localhost'),
        '-U', env('DB_USER'),
        '-d', env('DB_NAME'),
        '-v',
        '-f', str(backup_file)
    ]
    
    print(f"Starting backup to {backup_file}...")
    result = subprocess.run(cmd, env=env_vars, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Backup created successfully: {backup_file}")
        return backup_file
    else:
        print(f"✗ Backup failed: {result.stderr}")
        return None

if __name__ == '__main__':
    backup_database()