import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  BuscarAdministradoResponse,
  CaptchaResponse,
  LoginAdminResponse,
  ConsultaAutomaticaRequest
} from '../models/mtc-admin.models';

@Injectable({
  providedIn: 'root'
})
export class MtcAdminService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl; // e.g. /api/v1

  /**
   * Consulta automática completa en un solo llamado:
   * 1. Resuelve captcha con OCR (o manual si se provee)
   * 2. Si la sesión ya está activa (~50 min), omite el captcha
   * 3. Búsqueda y retorno de la ficha del administrado
   */
  consultaAutomatica(payload: ConsultaAutomaticaRequest): Observable<BuscarAdministradoResponse> {
    return this.http.post<BuscarAdministradoResponse>(
      `${this.baseUrl}/consulta-automatica`,
      payload
    );
  }

  /**
   * Consulta si las credenciales de sesión temporal MTC están activas
   */
  consultarEstadoSesion(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/session-status`);
  }

  /**
   * Invalida la sesión MTC en memoria para forzar un nuevo login
   */
  cerrarSesion(): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/logout-session`, {});
  }

  /**
   * Obtiene un captcha nuevo del MTC y opcionalmente resuelve el OCR
   */
  obtenerCaptcha(autoResolve: boolean = true): Observable<CaptchaResponse> {
    return this.http.post<CaptchaResponse>(
      `${this.baseUrl}/captcha?auto_resolve=${autoResolve}`,
      {}
    );
  }

  /**
   * Login paso a paso contra el portal del MTC
   */
  login(payload: {
    username: string;
    password: string;
    captcha_text?: string;
    captcha_key?: string;
    is_automatic: boolean;
  }): Observable<LoginAdminResponse> {
    return this.http.post<LoginAdminResponse>(`${this.baseUrl}/login`, payload);
  }

  /**
   * Listado de roles del operador en MTC
   */
  obtenerRoles(token: string): Observable<{ success: boolean; data: any[] }> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
    return this.http.get<{ success: boolean; data: any[] }>(`${this.baseUrl}/roles`, { headers });
  }

  /**
   * Selección de rol administrativo
   */
  seleccionarRol(idRol: string | number, token: string): Observable<any> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
    return this.http.post<any>(
      `${this.baseUrl}/select-rol`,
      { idRol },
      { headers }
    );
  }

  /**
   * Búsqueda manual con token de rol ya obtenido
   */
  buscarAdministrado(termino: string, roleToken: string): Observable<BuscarAdministradoResponse> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${roleToken}`
    });
    return this.http.get<BuscarAdministradoResponse>(
      `${this.baseUrl}/buscar/${termino.trim()}`,
      { headers }
    );
  }
}
