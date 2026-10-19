import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { NotificacionesService } from '../../core/services/notificaciones.service';
import { ThemeService } from '../../core/services/theme.service';

export interface MinioObjeto {
  name: string;
  size_bytes: number;
  size_formatted: string;
  last_modified: string | null;
  etag: string;
  download_url: string;
  tipo: string;
}

@Component({
  selector: 'app-custodia-minio',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './custodia-minio.component.html'
})
export class CustodiaMinioComponent implements OnInit {
  private service = inject(NotificacionesService);
  private sanitizer = inject(DomSanitizer);
  public themeService = inject(ThemeService);

  // Signals de Estado
  loading = signal<boolean>(false);
  estadoMinio = signal<any>(null);
  objetos = signal<MinioObjeto[]>([]);
  filtroTipo = signal<string>('TODOS');
  busqueda = signal<string>('');
  toastMensaje = signal<string | null>(null);

  // Modal de Previsualización Criptográfica
  objetoSeleccionado = signal<MinioObjeto | null>(null);
  urlVisorSegura = signal<SafeResourceUrl | null>(null);
  modalVisorAbierto = signal<boolean>(false);

  // Modal de Subida Manual
  modalSubidaAbierto = signal<boolean>(false);
  archivoParaSubir = signal<File | null>(null);
  hashSha256Calculado = signal<string>('');
  tipoDocSubida = signal<string>('ANEXO_ADMINISTRATIVO');
  subiendoArchivo = signal<boolean>(false);

  // Métricas Computadas
  totalObjetos = computed(() => this.objetos().length);
  totalResoluciones = computed(() => this.objetos().filter(o => o.tipo === 'Resolución Directoral').length);
  totalCAD = computed(() => this.objetos().filter(o => o.tipo === 'Constancia CAD').length);
  totalCAL = computed(() => this.objetos().filter(o => o.tipo === 'Constancia CAL').length);

  objetosFiltrados = computed(() => {
    const q = this.busqueda().toLowerCase().trim();
    const tipo = this.filtroTipo();

    return this.objetos().filter(obj => {
      const coincideTipo = tipo === 'TODOS' || obj.tipo === tipo;
      const coincideBusqueda = !q || 
        obj.name.toLowerCase().includes(q) || 
        obj.tipo.toLowerCase().includes(q) || 
        obj.etag.toLowerCase().includes(q);
      return coincideTipo && coincideBusqueda;
    });
  });

  ngOnInit(): void {
    this.cargarDatosMinio();
  }

  cargarDatosMinio(): void {
    this.loading.set(true);
    this.service.obtenerEstadoMinio().subscribe({
      next: (est) => {
        this.estadoMinio.set(est);
        this.service.obtenerObjetosMinio().subscribe({
          next: (objs) => {
            this.objetos.set(objs);
            this.loading.set(false);
          },
          error: () => this.loading.set(false)
        });
      },
      error: () => {
        this.loading.set(false);
      }
    });
  }

  verificarYPoblarBoveda(): void {
    this.loading.set(true);
    this.service.poblarDocumentosFaltantes().subscribe({
      next: (res) => {
        this.mostrarToast(`Bóveda RustFS S3 sincronizada: ${res.documentos_poblados_nuevos} documentos generados y custodiados.`);
        this.cargarDatosMinio();
      },
      error: (err) => {
        this.loading.set(false);
        this.mostrarToast(`Error al sincronizar bóveda: ${err.message || err}`);
      }
    });
  }

  abrirVisor(obj: MinioObjeto): void {
    this.objetoSeleccionado.set(obj);
    this.urlVisorSegura.set(this.sanitizer.bypassSecurityTrustResourceUrl(obj.download_url));
    this.modalVisorAbierto.set(true);
  }

  cerrarVisor(): void {
    this.modalVisorAbierto.set(false);
    this.objetoSeleccionado.set(null);
    this.urlVisorSegura.set(null);
  }

  async onArchivoSeleccionado(event: any): Promise<void> {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.archivoParaSubir.set(file);
      try {
        const arrayBuffer = await file.arrayBuffer();
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        this.hashSha256Calculado.set(hashHex);
      } catch (e) {
        console.error('Error calculando hash SHA-256:', e);
      }
    } else {
      alert('Por favor seleccione un archivo PDF válido.');
    }
  }

  subirArchivo(): void {
    const file = this.archivoParaSubir();
    if (!file) return;

    this.subiendoArchivo.set(true);
    this.service.subirDocumentoMinio(file, this.tipoDocSubida()).subscribe({
      next: () => {
        this.subiendoArchivo.set(false);
        this.modalSubidaAbierto.set(false);
        this.archivoParaSubir.set(null);
        this.hashSha256Calculado.set('');
        this.mostrarToast('Documento custodiado con éxito en el bucket RustFS S3.');
        this.cargarDatosMinio();
      },
      error: (err) => {
        this.subiendoArchivo.set(false);
        alert(`Error al subir documento a RustFS: ${err.message || err}`);
      }
    });
  }

  copiarAlPortapapeles(texto: string, label: string = 'Texto'): void {
    navigator.clipboard.writeText(texto).then(() => {
      this.mostrarToast(`${label} copiado al portapapeles.`);
    });
  }

  private mostrarToast(msj: string): void {
    this.toastMensaje.set(msj);
    setTimeout(() => {
      this.toastMensaje.set(null);
    }, 4000);
  }
}
