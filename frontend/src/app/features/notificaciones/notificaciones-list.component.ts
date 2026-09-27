import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NotificacionesService } from '../../core/services/notificaciones.service';
import { EstadoNotificacion } from '../../core/models/notificacion.model';

@Component({
  selector: 'app-notificaciones-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './notificaciones-list.component.html'
})
export class NotificacionesListComponent implements OnInit {
  public service = inject(NotificacionesService);

  ngOnInit(): void {
    this.recargar();
  }

  recargar(): void {
    this.service.cargarNotificaciones().subscribe();
  }

  firmar(notificacionId: string): void {
    if (confirm('¿Desea enviar este acto administrativo al servicio de firma digital del MTC?')) {
      this.service.firmarDigitalmente(notificacionId).subscribe({
        next: () => alert('Documento firmado con éxito por el servicio MTC.'),
        error: (err) => alert(`Error al firmar: ${err}`)
      });
    }
  }

  depositar(notificacionId: string): void {
    if (confirm('¿Confirma el depósito legal de la notificación en la Casilla Electrónica MTC del destinatario?')) {
      this.service.depositarEnCasilla(notificacionId).subscribe({
        next: () => alert('Notificación depositada formalmente en la Casilla MTC.'),
        error: (err) => alert(`Error al depositar: ${err}`)
      });
    }
  }

  sincronizar(notificacionId: string): void {
    this.service.sincronizarConstancias(notificacionId).subscribe({
      next: (actualizada) => {
        if (actualizada.estado === 'LEIDO_NOTIFICADO') {
          alert('¡El administrado ya leyó la notificación! Se descargó y custodió el Acuse de Lectura oficial.');
        } else {
          alert('La notificación sigue en estado DEPOSITADO. Aún no ha sido abierta por el administrado.');
        }
      },
      error: (err) => alert(`Error al sincronizar con MTC: ${err}`)
    });
  }

  getBadgeClass(estado: EstadoNotificacion): string {
    switch (estado) {
      case 'BORRADOR': return 'badge-borrador';
      case 'PENDIENTE_FIRMA': return 'badge-pendiente';
      case 'FIRMADO': return 'badge-firmado';
      case 'DEPOSITADO': return 'badge-depositado';
      case 'LEIDO_NOTIFICADO': return 'badge-leido';
      default: return 'badge-error';
    }
  }
}
