import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path
from app.services.backup_service import BackupService
from app.services.scheduler_service import SchedulerService
import logging

class BackupWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HC_RPAS_BackupService"
    _svc_display_name_ = "HC RPAS Backup Service"
    _svc_description_ = "Service de sauvegarde automatique pour HC RPAS"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.scheduler = None
        
        # Configuration des logs
        log_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=str(log_dir / "backup_service.log"),
            filemode="a"
        )
        self.logger = logging.getLogger('BackupWindowsService')

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.scheduler:
            self.scheduler.stop()

    def SvcDoRun(self):
        try:
            self.logger.info('Service démarré')
            backup_service = BackupService()
            self.scheduler = SchedulerService()
            
            # Première sauvegarde
            backup_path = backup_service.create_backup()
            if backup_path:
                self.logger.info(f'Sauvegarde initiale créée: {backup_path}')
            
            # Démarrage du planificateur
            self.scheduler.start(backup_service)
            self.logger.info('Planificateur démarré')
            
            # Attente du signal d'arrêt
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            
        except Exception as e:
            self.logger.error(f'Erreur dans le service: {str(e)}')
            if self.scheduler:
                self.scheduler.stop()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BackupWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BackupWindowsService)
