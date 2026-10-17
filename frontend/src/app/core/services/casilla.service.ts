import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpBackend } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { InfoCasillaResponse } from '../models/casilla.models';
import { environment } from '../../../environments/environment';

/** ============================================================
 *  CasillaService
 *  Encapsula las llamadas al API de Casillas Electrónicas
 *  (Node-RED) de la DRTC Puno, con aislamiento de interceptores.
 * ============================================================ */
@Injectable({ providedIn: 'root' })
export class CasillaService {
  private httpBackend = inject(HttpBackend);
  // Cliente HTTP aislado: no inyecta tokens de SIRRETT ni redirige al login si falla la red externa
  private rawHttp = new HttpClient(this.httpBackend);
  private http = inject(HttpClient);

  private readonly baseUrl = environment.mtcCasillaUrl || 'https://mtc.transportespuno.gob.pe/api/v2';
  private readonly apiKey = environment.mtcApiKey || 'topSecret123';
  private readonly proxyUrl = `${environment.apiUrl}/casilla/verificar`;

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'x-api-key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Paso 1 – Verificar existencia y estado de la casilla del administrado.
   * Consulta al API Node-RED y cuenta con fallback transparente en caso de CORS o firewall.
   */
  verificarEstado(tipoPers: string, tipoDoc: string, numDoc: string): Observable<InfoCasillaResponse> {
    const params = new HttpParams()
      .set('codTipoPersona', tipoPers)
      .set('codTipoDocumento', tipoDoc)
      .set('nroDocumento', numDoc);

    // Intentamos la llamada directa con el cliente aislado
    return this.rawHttp.get<InfoCasillaResponse>(`${this.baseUrl}/info`, {
      headers: this.getHeaders(),
      params
    }).pipe(
      catchError((err) => {
        console.warn('[CasillaService] Consulta directa interceptada (posible CORS / firewall). Recurriendo al puente seguro...', err);
        // Fallback al backend local para evitar problemas de CORS en navegador
        return this.http.get<InfoCasillaResponse>(this.proxyUrl, { params });
      })
    );
  }
}
