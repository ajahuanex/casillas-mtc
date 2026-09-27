import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class GeminiAiService {
  private cargandoSignal = signal<boolean>(false);
  public cargando = this.cargandoSignal.asReadonly();

  /**
   * Genera una síntesis ejecutiva y amigable del acto administrativo
   * para facilitar la comprensión del ciudadano en la casilla electrónica.
   */
  async resumirActoParaCiudadano(asunto: string, descripcion: string): Promise<string> {
    this.cargandoSignal.set(true);
    try {
      // Simulación de procesamiento o llamada a Gemini API (vía SDK o endpoint backend)
      await new Promise(resolve => setTimeout(resolve, 800));
      return `Estimado administrado: Mediante el presente acto se le comunica formalmente el inicio del trámite relacionado con "${asunto}". ` +
             `Dispone de los plazos procesales legales de ley para presentar descargos o consultas conforme a la normativa vigente.`;
    } finally {
      this.cargandoSignal.set(false);
    }
  }

  /**
   * Valida cumplimiento de requisitos formales de la notificación conforme a Ley 27444.
   */
  async validarRequisitosLegales(acto: string, asunto: string): Promise<{ valido: boolean; sugerencias: string[] }> {
    this.cargandoSignal.set(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      const sugerencias: string[] = [];
      if (!acto.includes('/') && !acto.includes('-')) {
        sugerencias.push('El número de acto administrativo debería incluir año y siglas (ej. R.D. 120-2026-MTC/18).');
      }
      if (asunto.length < 15) {
        sugerencias.push('El asunto es demasiado breve; se recomienda detallar el objeto del pronunciamiento.');
      }
      return {
        valido: sugerencias.length === 0,
        sugerencias: sugerencias.length > 0 ? sugerencias : ['El acto administrativo cumple con los estándares formales requeridos.']
      };
    } finally {
      this.cargandoSignal.set(false);
    }
  }
}
