from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Optimize PostgreSQL database by running VACUUM ANALYZE and REINDEX'
    
    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                self.stdout.write(self.style.WARNING("Running VACUUM ANALYZE... (This might take a moment)"))
                # Note: VACUUM cannot run inside a transaction block in Postgres
                connection.set_autocommit(True)
                cursor.execute("VACUUM ANALYZE;")
                self.stdout.write(self.style.SUCCESS("✓ VACUUM ANALYZE completed"))
                
                self.stdout.write(self.style.WARNING("Reindexing database..."))
                cursor.execute("REINDEX DATABASE restaurant_portal;")
                self.stdout.write(self.style.SUCCESS("✓ Database reindexed successfully"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Optimization failed: {e}"))