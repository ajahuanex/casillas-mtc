import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { NotificacionesService } from '../../core/services/notificaciones.service';
import { GeminiAiService } from '../../core/services/gemini-ai.service';
import { TipoDocumentoIdentidad } from '../../core/models/notificacion.model';

@Component({
  selector: 'app-notificacion-create',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './notificacion-create.component.html'
})
export class NotificacionCreateComponent {
  public service = inject(NotificacionesService);
  public gemini = inject(GeminiAiService);
  private router = inject(Router);

  codigoExpediente: string = '';
  numeroActo: string = '';
  asunto: string = '';
  descripcion: string = '';
  
  tipoDocumento: TipoDocumentoIdentidad = 'DNI';
  numeroDocumento: string = '';
  nombreDestinatario: string = '';
  
  // Estado de verificación en MTC
  casillaVerificada = signal<boolean | null>(null);
  verificandoCasilla = signal<boolean>(false);
  mensajeCasilla = signal<string>('');

  // Sugerencias Gemini AI
  sugerenciasIa = signal<string[]>([]);
  iaActiva = signal<boolean>(false);

  archivoSeleccionado: File | null = null;

  verificarCasillaMTC(): void {
    if (!this.numeroDocumento || this.numeroDocumento.length < 8) {
      alert('Por favor ingrese un número de documento válido antes de verificar.');
      return;
    }

    this.verificandoCasilla.set(true);
    this.casillaVerificada.set(null);
    this.mensajeCasilla.set('');

    const codTipoDoc = this.tipoDocumento === 'DNI' ? '00002' : '00001';

    this.service.verificarCasilla(this.numeroDocumento, '00001', codTipoDoc).subscribe({
      next: (res) => {
        this.verificandoCasilla.set(false);
        const info = res.info;
        const esExitoso = res.status === 'exitoso' || info?.success === true;
        const estaActivo = info?.data?.activo === true;

        if (esExitoso && estaActivo) {
          this.casillaVerificada.set(true);
          this.mensajeCasilla.set(`✓ Casilla activa en MTC / DRTC`);
          if (info.data?.nombreCompleto && !this.nombreDestinatario) {
            this.nombreDestinatario = info.data.nombreCompleto;
          }
        } else {
          this.casillaVerificada.set(false);
          this.mensajeCasilla.set(info?.message || 'El administrado no tiene casilla activa.');
        }
      },
      error: (err) => {
        this.verificandoCasilla.set(false);
        this.casillaVerificada.set(false);
        this.mensajeCasilla.set('Error conectando con el servicio de casillas.');
      }
    });
  }

  async consultarGeminiAI(): Promise<void> {
    if (!this.asunto) {
      alert('Por favor complete el Asunto para que Gemini AI pueda asistirle.');
      return;
    }
    this.iaActiva.set(true);
    const validacion = await this.gemini.validarRequisitosLegales(this.numeroActo, this.asunto);
    this.sugerenciasIa.set(validacion.sugerencias);
    if (!this.descripcion) {
      this.descripcion = await this.gemini.resumirActoParaCiudadano(this.asunto, this.descripcion);
    }
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.archivoSeleccionado = file;
    } else {
      alert('Por favor selecciona un archivo PDF válido.');
      this.archivoSeleccionado = null;
    }
  }

  guardar(): void {
    if (!this.archivoSeleccionado) {
      alert('Debes adjuntar el documento PDF del acto administrativo.');
      return;
    }

    this.service.crearNotificacion({
      codigo_expediente: this.codigoExpediente,
      numero_acto_administrativo: this.numeroActo,
      asunto: this.asunto,
      descripcion: this.descripcion,
      tipo_documento_destinatario: this.tipoDocumento,
      numero_documento_destinatario: this.numeroDocumento,
      nombre_destinatario: this.nombreDestinatario,
      archivo: this.archivoSeleccionado
    }).subscribe({
      next: () => {
        alert('Notificación registrada exitosamente en MinIO S3 y PostgreSQL.');
        this.router.navigate(['/']);
      },
      error: (err) => {
        alert(`Error al registrar notificación: ${err}`);
      }
    });
  }
}
