from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Check database health, active connections, and cache hit ratio'
    
    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # 1. Check connection and version
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"✓ Connected to PostgreSQL\n  Version: {version.split(',')[0]}"))
                
                # 2. Check active connections
                cursor.execute("""
                    SELECT datname, numbackends 
                    FROM pg_stat_database 
                    WHERE datname = current_database();
                """)
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS(f"✓ Active Connections: {result[1]}"))
                
                # 3. Check cache hit ratio
                cursor.execute("""
                    SELECT 
                        SUM(heap_blks_read) as blocks_read,
                        SUM(heap_blks_hit) as blocks_hit,
                        ROUND(100 * SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit) + SUM(heap_blks_read), 0), 2) as ratio
                    FROM pg_statio_user_tables;
                """)
                result = cursor.fetchone()
                if result and result[2] is not None:
                    self.stdout.write(self.style.SUCCESS(f"✓ Cache Hit Ratio: {result[2]}%"))
                else:
                    self.stdout.write(self.style.WARNING("Cache Hit Ratio: No data yet (run queries first)"))
                    
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f"✗ Database connection failed: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Health check failed: {e}"))