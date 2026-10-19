export type TipoDocumentoIdentidad = 'DNI' | 'RUC' | 'CE' | 'PASAPORTE';
export type EstadoCasilla = 'ACTIVA' | 'SUSPENDIDA' | 'NO_HABILITADA';
export type EstadoNotificacion = 
  | 'BORRADOR' 
  | 'PENDIENTE_FIRMA' 
  | 'FIRMADO' 
  | 'EN_COLA_DEPOSITO' 
  | 'DEPOSITADO' 
  | 'LEIDO_NOTIFICADO' 
  | 'NOTIFICADO_POR_PLAZO' 
  | 'ERROR_ENVIO';

export type TipoDocumentoAdjunto = 'ACTO_ADMINISTRATIVO_ORIGINAL' | 'DOCUMENTO_FIRMADO' | 'ANEXO';
export type TipoAcuse = 'DEPOSITO' | 'LECTURA_NOTIFICACION';

export interface DocumentoNotificacion {
  id: string;
  tipo_documento: TipoDocumentoAdjunto;
  nombre_archivo: string;
  storage_path: string;
  sha256_hash: string;
  tamanio_bytes: number;
  mime_type: string;
  created_at: string;
  download_url?: string;
}

export interface AcuseMTC {
  id: string;
  tipo_acuse: TipoAcuse;
  codigo_verificacion_mtc: string;
  storage_path: string;
  sha256_hash: string;
  fecha_hora_mtc: string;
  download_url?: string;
}

export interface CasillaMTC {
  id: string;
  codigo_casilla: string;
  estado_casilla: EstadoCasilla;
  ultima_verificacion?: string;
}

export interface Notificacion {
  id: string;
  codigo_expediente: string;
  numero_acto_administrativo: string;
  asunto: string;
  descripcion?: string;
  estado: EstadoNotificacion;
  fecha_emision: string;
  fecha_firma?: string;
  fecha_deposito?: string;
  fecha_lectura?: string;
  fecha_notificacion_efectiva?: string;
  fecha_limite_gracia_5dias?: string;
  fecha_inicio_computo?: string;
  fecha_vencimiento_plazo?: string;
  plazo_dias_habiles: number;
  tipo_procedimiento?: string;
  origen_notificacion_efectiva?: string;
  estado_plazo?: 'EN_PLAZO' | 'POR_VENCER_48H' | 'VENCE_HOY' | 'PLAZO_FENECIDO' | 'EN_GRACIA_LECTURA' | 'PENDIENTE_DEPOSITO' | string;
  dias_habiles_restantes?: number;
  porcentaje_transcurrido: number;
  id_transaccion_mtc?: string;
  casilla?: CasillaMTC;
  documentos: DocumentoNotificacion[];
  acuses: AcuseMTC[];
}

export interface CrearNotificacionPayload {
  codigo_expediente: string;
  numero_acto_administrativo: string;
  asunto: string;
  descripcion?: string;
  tipo_documento_destinatario: TipoDocumentoIdentidad;
  numero_documento_destinatario: string;
  nombre_destinatario: string;
  plazo_dias_habiles: number;
  tipo_procedimiento: string;
  archivo: File;
}

export interface DashboardKpis {
  total_notificaciones: number;
  en_plazo_ordinario: number;
  alerta_por_vencer_48h: number;
  plazo_vencido: number;
  notificadas_ficcion_legal: number;
  en_gracia_lectura: number;
}

export interface DashboardAlertasResponse {
  kpis: DashboardKpis;
  notificaciones: Notificacion[];
  hora_oficial_peru: string;
}

export interface VerificarCasillaResponse {
  success: boolean;
  numero_documento: string;
  tipo_persona: string;
  tipo_documento: string;
  tiene_casilla: boolean;
  codigo_casilla: string;
  estado_casilla: string;
  razon_social?: string;
  direccion?: string;
  correo?: string;
  telefono?: string;
  representante_legal?: string;
  servidor_host?: string;
  entorno?: string;
  mensaje: string;
  valido_para_notificar: boolean;
  domicilio_telematico_valido: boolean;
  normativa_aplicable: string;
}

