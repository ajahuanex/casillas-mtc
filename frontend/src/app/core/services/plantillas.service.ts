import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Plantilla {
  id: string;
  codigo: string; // ej. P-PAS-01
  nombre: string;
  categoria: 'FISCALIZADORA' | 'ADMINISTRATIVA' | 'IMPUGNATORIA' | 'COACTIVA';
  tipo_procedimiento: string;
  base_legal: string;
  asunto_predeterminado: string;
  plazo_dias_defecto: number;
  tipo_plazo: string;
  cuerpo_html_template: string;
  variables_requeridas: string[];
  organo_emisor_defecto: string;
  requiere_firma_digital: boolean;
  activo: boolean;
  version: number;
}

export interface PlantillaRenderResponse {
  codigo: string;
  nombre: string;
  asunto_renderizado: string;
  cuerpo_renderizado: string;
  plazo_dias: number;
  tipo_plazo: string;
  variables_faltantes: string[];
}

@Injectable({
  providedIn: 'root'
})
export class PlantillasService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/plantillas`;

  // Signals reactivos para Angular 22
  public plantillas = signal<Plantilla[]>([]);
  public plantillaSeleccionada = signal<Plantilla | null>(null);
  public cargando = signal<boolean>(false);
  public error = signal<string | null>(null);

  /**
   * Obtiene la lista completa de plantillas oficiales con filtro opcional por categoría
   */
  obtenerPlantillas(categoria?: string): Observable<Plantilla[]> {
    this.cargando.set(true);
    this.error.set(null);

    let params = new HttpParams();
    if (categoria && categoria !== 'TODAS') {
      params = params.set('categoria', categoria);
    }

    return this.http.get<Plantilla[]>(this.apiUrl, { params }).pipe(
      tap({
        next: (items) => {
          this.plantillas.set(items);
          this.cargando.set(false);
        },
        error: (err) => {
          this.error.set(err.message || 'Error al cargar plantillas');
          this.cargando.set(false);
        }
      })
    );
  }

  /**
   * Obtiene el detalle de una plantilla por su código P-*
   */
  obtenerPlantillaPorCodigo(codigo: string): Observable<Plantilla> {
    return this.http.get<Plantilla>(`${this.apiUrl}/${codigo}`).pipe(
      tap(item => this.plantillaSeleccionada.set(item))
    );
  }

  /**
   * Renderiza el template Jinja2 con las variables provistas
   */
  renderizar(codigo: string, variables: Record<string, any>): Observable<PlantillaRenderResponse> {
    return this.http.post<PlantillaRenderResponse>(`${this.apiUrl}/${codigo}/render`, { variables });
  }
}
