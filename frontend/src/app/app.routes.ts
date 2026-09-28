import { Routes } from '@angular/router';
import { DashboardAlertasComponent } from './features/dashboard/dashboard-alertas.component';
import { NotificacionesListComponent } from './features/notificaciones/notificaciones-list.component';
import { NotificacionCreateComponent } from './features/notificaciones/notificacion-create.component';
import { CustodiaMinioComponent } from './features/custodia-minio/custodia-minio.component';

export const routes: Routes = [
  {
    path: '',
    component: DashboardAlertasComponent,
    title: 'Control de Tiempos y Alertas - Casilla MTC'
  },
  {
    path: 'dashboard',
    component: DashboardAlertasComponent,
    title: 'Control de Tiempos y Alertas - Casilla MTC'
  },
  {
    path: 'custodia',
    component: CustodiaMinioComponent,
    title: 'Bóveda MinIO S3 & Custodia Criptográfica - DRTC Puno'
  },
  {
    path: 'bandeja',
    component: NotificacionesListComponent,
    title: 'Bandeja General de Notificaciones - Casilla MTC'
  },
  {
    path: 'nueva',
    component: NotificacionCreateComponent,
    title: 'Nueva Emisión y Validación - Casilla MTC'
  },

  {
    path: '**',
    redirectTo: ''
  }
];
