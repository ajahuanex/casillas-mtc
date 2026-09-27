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
  fecha_notificacion_efectiva?: string;
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
  archivo: File;
}
