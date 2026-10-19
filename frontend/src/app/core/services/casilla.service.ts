import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpBackend } from '@angular/common/http';
import { Observable, catchError } from 'rxjs';
import { InfoCasillaResponse } from '../models/casilla.models';
import { environment } from '../../../environments/environment';

/** ============================================================
 *  CasillaService
 *  Encapsula las llamadas al API de Casillas Electrónicas
 *  (Node-RED) de la DRTC Puno, con conmutador de entorno
 *  (Desarrollo vs Producción) y aislamiento de interceptores.
 * ============================================================ */
@Injectable({ providedIn: 'root' })
export class CasillaService {
  private httpBackend = inject(HttpBackend);
  private rawHttp = new HttpClient(this.httpBackend);
  private http = inject(HttpClient);

  // Switch de entorno reactivo: 'desarrollo' o 'produccion'
  entornoActivo = signal<'desarrollo' | 'produccion'>('desarrollo');

  private readonly devUrl = 'https://casillas.transportespuno.gob.pe/api/v2';
  private readonly prodUrl = 'https://mtc.transportespuno.gob.pe/api/v2';
  private readonly apiKey = environment.mtcApiKey || 'topSecret123';
  private readonly proxyUrl = `${environment.apiUrl}/casilla/verificar`;

  getBaseUrl(): string {
    return this.entornoActivo() === 'produccion' ? this.prodUrl : this.devUrl;
  }

  setEntorno(entorno: 'desarrollo' | 'produccion'): void {
    this.entornoActivo.set(entorno);
  }

  toggleEntorno(): void {
    this.entornoActivo.set(this.entornoActivo() === 'desarrollo' ? 'produccion' : 'desarrollo');
  }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'x-api-key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Paso 1 – Verificar existencia y estado de la casilla del administrado con switch de entorno.
   * Conecta a través del puente seguro backend que resuelve en caliente contra:
   * - Desarrollo: casillas.transportespuno.gob.pe
   * - Producción: mtc.transportespuno.gob.pe
   */
  verificarEstado(tipoPers: string, tipoDoc: string, numDoc: string): Observable<InfoCasillaResponse> {
    const modo = this.entornoActivo();
    const params = new HttpParams()
      .set('codTipoPersona', tipoPers)
      .set('codTipoDocumento', tipoDoc)
      .set('nroDocumento', numDoc)
      .set('entorno', modo);

    return this.http.get<InfoCasillaResponse>(this.proxyUrl, { params });
  }
}
