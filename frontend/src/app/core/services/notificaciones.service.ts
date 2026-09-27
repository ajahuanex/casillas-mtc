import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Notificacion, CrearNotificacionPayload, EstadoNotificacion } from '../models/notificacion.model';

@Injectable({
  providedIn: 'root'
})
export class NotificacionesService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1/notificaciones';

  // Signals para gestión reactiva del estado
  private notificacionesSignal = signal<Notificacion[]>([]);
  private loadingSignal = signal<boolean>(false);
  private errorSignal = signal<string | null>(null);

  // Selectores públicos computados (Read-only Signals)
  public notificaciones = computed(() => this.notificacionesSignal());
  public loading = computed(() => this.loadingSignal());
  public error = computed(() => this.errorSignal());

  // Métricas de estado en tiempo real
  public totalNotificaciones = computed(() => this.notificacionesSignal().length);
  public totalBorradores = computed(() => 
    this.notificacionesSignal().filter(n => n.estado === 'BORRADOR').length
  );
  public totalFirmadas = computed(() => 
    this.notificacionesSignal().filter(n => n.estado === 'FIRMADO').length
  );
  public totalDepositadas = computed(() => 
    this.notificacionesSignal().filter(n => n.estado === 'DEPOSITADO').length
  );
  public totalLeidas = computed(() => 
    this.notificacionesSignal().filter(n => n.estado === 'LEIDO_NOTIFICADO').length
  );

  verificarCasilla(numeroDocumento: string, tipoPersona: string = '00001', tipoDocumento: string = '00002') {
    const params = new HttpParams()
      .set('numero_documento', numeroDocumento)
      .set('tipo_persona', tipoPersona)
      .set('tipo_documento', tipoDocumento);

    return this.http.get<any>(`${this.apiUrl}/verificar-casilla`, { params });
  }

  cargarNotificaciones(estado?: EstadoNotificacion, codigoExpediente?: string): Observable<Notificacion[]> {
    this.loadingSignal.set(true);
    this.errorSignal.set(null);

    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    if (codigoExpediente) params = params.set('codigo_expediente', codigoExpediente);

    return this.http.get<Notificacion[]>(this.apiUrl, { params }).pipe(
      tap({
        next: (data) => {
          this.notificacionesSignal.set(data);
          this.loadingSignal.set(false);
        },
        error: (err) => {
          this.errorSignal.set(err.message || 'Error al cargar notificaciones');
          this.loadingSignal.set(false);
        }
      })
    );
  }

  crearNotificacion(payload: CrearNotificacionPayload): Observable<Notificacion> {
    this.loadingSignal.set(true);
    const formData = new FormData();
    formData.append('codigo_expediente', payload.codigo_expediente);
    formData.append('numero_acto_administrativo', payload.numero_acto_administrativo);
    formData.append('asunto', payload.asunto);
    if (payload.descripcion) formData.append('descripcion', payload.descripcion);
    formData.append('tipo_documento_destinatario', payload.tipo_documento_destinatario);
    formData.append('numero_documento_destinatario', payload.numero_documento_destinatario);
    formData.append('nombre_destinatario', payload.nombre_destinatario);
    formData.append('archivo', payload.archivo);

    return this.http.post<Notificacion>(this.apiUrl, formData).pipe(
      tap({
        next: (nueva) => {
          this.notificacionesSignal.update(lista => [nueva, ...lista]);
          this.loadingSignal.set(false);
        },
        error: (err) => {
          this.errorSignal.set(err.message || 'Error al crear notificación');
          this.loadingSignal.set(false);
        }
      })
    );
  }

  firmarDigitalmente(notificacionId: string): Observable<Notificacion> {
    this.loadingSignal.set(true);
    return this.http.post<Notificacion>(`${this.apiUrl}/${notificacionId}/firmar`, {}).pipe(
      tap({
        next: (actualizada) => {
          this.notificacionesSignal.update(lista => 
            lista.map(item => item.id === actualizada.id ? actualizada : item)
          );
          this.loadingSignal.set(false);
        },
        error: (err) => {
          this.errorSignal.set(err.message || 'Error en firma digital MTC');
          this.loadingSignal.set(false);
        }
      })
    );
  }

  depositarEnCasilla(notificacionId: string, idCategoria: number = 5): Observable<Notificacion> {
    this.loadingSignal.set(true);
    let params = new HttpParams().set('id_categoria', idCategoria.toString());
    return this.http.post<Notificacion>(`${this.apiUrl}/${notificacionId}/depositar`, {}, { params }).pipe(
      tap({
        next: (actualizada) => {
          this.notificacionesSignal.update(lista => 
            lista.map(item => item.id === actualizada.id ? actualizada : item)
          );
          this.loadingSignal.set(false);
        },
        error: (err) => {
          this.errorSignal.set(err.message || 'Error al depositar en casilla MTC');
          this.loadingSignal.set(false);
        }
      })
    );
  }

  sincronizarConstancias(notificacionId: string): Observable<Notificacion> {
    this.loadingSignal.set(true);
    return this.http.post<Notificacion>(`${this.apiUrl}/${notificacionId}/sincronizar-constancias`, {}).pipe(
      tap({
        next: (actualizada) => {
          this.notificacionesSignal.update(lista => 
            lista.map(item => item.id === actualizada.id ? actualizada : item)
          );
          this.loadingSignal.set(false);
        },
        error: (err) => {
          this.errorSignal.set(err.message || 'Error al sincronizar constancias con MTC');
          this.loadingSignal.set(false);
        }
      })
    );
  }
}
