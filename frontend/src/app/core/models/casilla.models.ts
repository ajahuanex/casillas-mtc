/**
 * Modelos de datos para la integración con el API de Casillas Electrónicas
 * (Node-RED) de la DRTC Puno / MTC.
 */

export interface CasillaData {
  activo: boolean;
  codigoCasilla?: string;
  nombreCompleto?: string;
  razonSocial?: string;
  correo?: string;
  telefono?: string;
  direccion?: string;
  representanteLegal?: string;
  estadoDomiciliacion?: string;
  entorno?: string;
  servidorHost?: string;
  ubigeo?: string;
  fechaCreacion?: string;
  [key: string]: any;
}

export interface CasillaInfo {
  success: boolean;
  message: string;
  entorno?: string;
  servidorHost?: string;
  data: CasillaData;
  errors?: any;
}

export interface InfoCasillaResponse {
  status: string;
  info: CasillaInfo;
  data?: CasillaData;
  [key: string]: any;
}
