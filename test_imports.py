try:
    print("Test des imports...")
    
    print("1. Import BackupService...")
    from app.services.backup_service import BackupService
    print("OK")
    
    print("2. Import SchedulerService...")
    from app.services.scheduler_service import SchedulerService
    print("OK")
    
    print("3. Test création BackupService...")
    backup = BackupService()
    print("OK")
    
    print("4. Test création SchedulerService...")
    scheduler = SchedulerService()
    print("OK")
    
    print("\nTous les tests ont réussi!")
    
except Exception as e:
    print(f"\nErreur: {str(e)}")
