import { Routes } from '@angular/router';
import { NotificacionesListComponent } from './features/notificaciones/notificaciones-list.component';
import { NotificacionCreateComponent } from './features/notificaciones/notificacion-create.component';

export const routes: Routes = [
  {
    path: '',
    component: NotificacionesListComponent,
    title: 'Bandeja de Notificaciones - Casilla MTC'
  },
  {
    path: 'nueva',
    component: NotificacionCreateComponent,
    title: 'Nueva Notificación - Casilla MTC'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
