export interface AdministradoItem {
  idPersona?: number;
  nroDocumento?: string;
  ruc?: string;
  nombreCompleto?: string;
  razonSocial?: string;
  codTipoPersona?: string;
  nombreTipoPersona?: string;
  correoElectronico?: string;
  estado?: boolean;
  username?: string;
}

export interface BuscarAdministradoData {
  datos: AdministradoItem[];
  total: number;
}

export interface SessionStatus {
  activa: boolean;
  username?: string;
  idRol?: string;
  segundos_restantes: number;
  minutos_restantes: number;
  creado_en?: string;
  token_presente: boolean;
}

export interface BuscarAdministradoResponse {
  success: boolean;
  message: string;
  data: BuscarAdministradoData;
  session?: SessionStatus;
}

export interface CaptchaResponse {
  img: string;
  key: string;
  resolved_text?: string;
}

export interface RolItem {
  idRol: string | number;
  nombre?: string;
  descripcion?: string;
  estado?: boolean;
  [key: string]: any;
}

export interface LoginAdminResponse {
  success: boolean;
  accessToken?: string;
  refreshToken?: string;
  errorMessage?: string;
}

export interface ConsultaAutomaticaRequest {
  target_doc: string;
  username?: string;
  password?: string;
  id_rol?: string | number;
  captcha_text?: string;
  captcha_key?: string;
  force_refresh?: boolean;
}
