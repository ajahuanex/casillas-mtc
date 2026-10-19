import { Component, signal, computed, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { MtcAdminService } from '../../core/services/mtc-admin.service';
import { CasillaService } from '../../core/services/casilla.service';
import { AdministradoItem, BuscarAdministradoResponse, SessionStatus } from '../../core/models/mtc-admin.models';

type ModoConsulta = 'automatico' | 'pasos' | 'casilla-local';
type TipoDoc = 'DNI' | 'RUC';

@Component({
  selector: 'app-consulta-administrados',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './consulta-administrados.component.html'
})
export class ConsultaAdministradosComponent implements OnInit {
  private mtcService = inject(MtcAdminService);
  public casillaService = inject(CasillaService);
  private router = inject(Router);

  // Estados reactivos con Signals
  modoActivo = signal<ModoConsulta>('automatico');
  tipoDoc = signal<TipoDoc>('RUC');
  documentoBusqueda = signal<string>('20363914994');

  // Credenciales operador MTC
  usuarioOperador = signal<string>('40396522');
  claveOperador = signal<string>('Ajahuana40396522%');
  idRolSeleccionado = signal<string>('1');

  // Estado de Sesión en Caché (1 hora de vigencia)
  sessionStatus = signal<SessionStatus | null>(null);

  // Modo Manual de Captcha
  mostrarInputManual = signal<boolean>(false);
  captchaManualImg = signal<string | null>(null);
  captchaManualKey = signal<string | null>(null);
  captchaManualTexto = signal<string>('');
  cargandoCaptchaManual = signal<boolean>(false);

  // Estados de carga y progreso
  cargando = signal<boolean>(false);
  etapaProgreso = signal<string>('');
  errorMensaje = signal<string | null>(null);
  tiempoEjecucion = signal<number>(0);

  // Resultados
  resultado = signal<BuscarAdministradoResponse | null>(null);
  administradoSeleccionado = computed<AdministradoItem | null>(() => {
    const res = this.resultado();
    if (res && res.data && res.data.datos && res.data.datos.length > 0) {
      return res.data.datos[0];
    }
    return null;
  });

  // Estado del Laboratorio Paso a Paso
  captchaImg = signal<string | null>(null);
  captchaKey = signal<string | null>(null);
  captchaTextoResuelto = signal<string>('');
  loginToken = signal<string | null>(null);
  rolesDisponibles = signal<any[]>([]);
  roleToken = signal<string | null>(null);
  modalJsonAbierto = signal<boolean>(false);
  copiadoExitoso = signal<boolean>(false);

  // Consultas Rápidas
  presets = [
    { label: 'DRTC Puno (RUC)', doc: '20363914994', tipo: 'RUC' as TipoDoc, desc: 'Dir. Regional de Transportes' },
    { label: 'Beto Portillo (DNI)', doc: '42455198', tipo: 'DNI' as TipoDoc, desc: 'Titular / Administrado' },
    { label: 'Operador (DNI)', doc: '40396522', tipo: 'DNI' as TipoDoc, desc: 'Operador MTC Puno' }
  ];

  ngOnInit(): void {
    this.cargarEstadoSesion();
  }

  cargarEstadoSesion(): void {
    this.mtcService.consultarEstadoSesion().subscribe({
      next: (status) => {
        this.sessionStatus.set(status);
      },
      error: (err) => {
        console.debug('[MTCAdmin] No se pudo verificar estado de sesión:', err);
      }
    });
  }

  cerrarSesionMtc(): void {
    this.mtcService.cerrarSesion().subscribe({
      next: () => {
        this.sessionStatus.set(null);
        this.errorMensaje.set(null);
        this.cargarEstadoSesion();
      }
    });
  }

  cambiarTipoDoc(tipo: TipoDoc): void {
    this.tipoDoc.set(tipo);
    if (tipo === 'RUC' && this.documentoBusqueda().length === 8) {
      this.documentoBusqueda.set('20363914994');
    } else if (tipo === 'DNI' && this.documentoBusqueda().length === 11) {
      this.documentoBusqueda.set('42455198');
    }
  }

  seleccionarPreset(preset: { doc: string; tipo: TipoDoc }): void {
    this.tipoDoc.set(preset.tipo);
    this.documentoBusqueda.set(preset.doc);
    this.ejecutarConsulta();
  }

  solicitarCaptchaManual(): void {
    this.cargandoCaptchaManual.set(true);
    this.errorMensaje.set(null);
    this.mtcService.obtenerCaptcha(false).subscribe({
      next: (data) => {
        this.captchaManualImg.set(data.img);
        this.captchaManualKey.set(data.key);
        this.captchaManualTexto.set('');
        this.mostrarInputManual.set(true);
        this.cargandoCaptchaManual.set(false);
      },
      error: (err) => {
        this.cargandoCaptchaManual.set(false);
        this.errorMensaje.set(`No se pudo obtener nuevo Captcha del MTC: ${err.message}`);
      }
    });
  }

  ejecutarConsulta(usarManual: boolean = false): void {
    const doc = this.documentoBusqueda().trim();
    if (!doc) {
      this.errorMensaje.set('Ingrese un número de documento válido (DNI o RUC).');
      return;
    }

    if (usarManual && !this.captchaManualTexto().trim()) {
      this.errorMensaje.set('Por favor ingrese los caracteres del Captcha visible en la imagen.');
      return;
    }

    this.cargando.set(true);
    this.errorMensaje.set(null);
    this.resultado.set(null);
    const inicio = Date.now();

    const sesionActiva = this.sessionStatus()?.activa;

    if (sesionActiva) {
      this.etapaProgreso.set('Reutilizando credenciales de sesión MTC activas (sin Captcha)...');
    } else if (usarManual) {
      this.etapaProgreso.set('Validando Captcha manual y autenticando con MTC...');
    } else {
      this.etapaProgreso.set('1/3 Solicitando imagen de Captcha al MTC...');
    }

    const t1 = setTimeout(() => {
      if (this.cargando() && !sesionActiva) {
        this.etapaProgreso.set('2/3 Aplicando visión artificial OCR...');
      }
    }, 1200);

    const t2 = setTimeout(() => {
      if (this.cargando() && !sesionActiva) {
        this.etapaProgreso.set('3/3 Autenticando sesión y recuperando ficha oficial...');
      }
    }, 2800);

    const payload: any = {
      target_doc: doc,
      username: this.usuarioOperador(),
      password: this.claveOperador(),
      id_rol: this.idRolSeleccionado()
    };

    if (usarManual && this.captchaManualTexto()) {
      payload.captcha_text = this.captchaManualTexto().trim();
      payload.captcha_key = this.captchaManualKey();
    }

    this.mtcService.consultaAutomatica(payload).subscribe({
      next: (res) => {
        clearTimeout(t1);
        clearTimeout(t2);
        this.tiempoEjecucion.set(Math.round((Date.now() - inicio) / 100) / 10);
        this.resultado.set(res);
        if (res.session) {
          this.sessionStatus.set(res.session);
        } else {
          this.cargarEstadoSesion();
        }
        this.mostrarInputManual.set(false);
        this.cargando.set(false);
        this.etapaProgreso.set('');
      },
      error: (err) => {
        clearTimeout(t1);
        clearTimeout(t2);
        this.cargando.set(false);
        this.etapaProgreso.set('');
        
        const detail = err.error?.detail;
        if (detail && typeof detail === 'object' && detail.requires_manual_captcha) {
          this.errorMensaje.set(detail.message || 'El OCR no pudo validar el Captcha. Ingréselo manualmente.');
          this.captchaManualImg.set(detail.captcha_img);
          this.captchaManualKey.set(detail.captcha_key);
          this.captchaManualTexto.set('');
          this.mostrarInputManual.set(true);
        } else {
          const msg = typeof detail === 'string' ? detail : err.message || 'Error en comunicación con MTC';
          this.errorMensaje.set(`Aviso: ${msg}`);
        }
      }
    });
  }

  // --- MÉTODOS PARA EL LABORATORIO PASO A PASO ---
  paso1ObtenerCaptcha(): void {
    this.cargando.set(true);
    this.errorMensaje.set(null);
    this.mtcService.obtenerCaptcha(true).subscribe({
      next: (data) => {
        this.captchaImg.set(data.img);
        this.captchaKey.set(data.key);
        this.captchaTextoResuelto.set(data.resolved_text || '');
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.errorMensaje.set(`Error obteniendo captcha: ${err.message}`);
      }
    });
  }

  paso2Login(): void {
    if (!this.captchaKey()) {
      this.errorMensaje.set('Primero debe obtener un captcha en el Paso 1.');
      return;
    }
    this.cargando.set(true);
    this.errorMensaje.set(null);
    this.mtcService.login({
      username: this.usuarioOperador(),
      password: this.claveOperador(),
      captcha_text: this.captchaTextoResuelto(),
      captcha_key: this.captchaKey()!,
      is_automatic: false
    }).subscribe({
      next: (data) => {
        this.loginToken.set(data.accessToken || null);
        this.cargando.set(false);
        if (data.accessToken) {
          this.paso3ListarRoles(data.accessToken);
        }
      },
      error: (err) => {
        this.cargando.set(false);
        this.errorMensaje.set(`Login rechazado: ${err.error?.detail || err.message}`);
      }
    });
  }

  paso3ListarRoles(token?: string): void {
    const t = token || this.loginToken();
    if (!t) return;
    this.mtcService.obtenerRoles(t).subscribe({
      next: (data) => {
        this.rolesDisponibles.set(data.data || []);
      },
      error: (err) => {
        console.warn('Roles error:', err);
      }
    });
  }

  paso4SeleccionarRol(): void {
    const t = this.loginToken();
    if (!t) {
      this.errorMensaje.set('No cuenta con token de login activo.');
      return;
    }
    this.cargando.set(true);
    this.mtcService.seleccionarRol(this.idRolSeleccionado(), t).subscribe({
      next: (data) => {
        this.roleToken.set(data.accessToken || t);
        this.cargando.set(false);
        this.cargarEstadoSesion();
      },
      error: (err) => {
        this.cargando.set(false);
        this.errorMensaje.set(`Error seleccionando rol: ${err.error?.detail || err.message}`);
      }
    });
  }

  paso5Buscar(): void {
    const rToken = this.roleToken() || this.loginToken();
    if (!rToken) {
      this.errorMensaje.set('Debe autenticarse y seleccionar rol primero.');
      return;
    }
    this.cargando.set(true);
    this.errorMensaje.set(null);
    this.mtcService.buscarAdministrado(this.documentoBusqueda(), rToken).subscribe({
      next: (res) => {
        this.resultado.set(res);
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.errorMensaje.set(`Error buscando administrado: ${err.error?.detail || err.message}`);
      }
    });
  }

  // --- ACCIONES RÁPIDAS ---
  copiarAlPortapapeles(texto?: string): void {
    if (!texto) return;
    navigator.clipboard.writeText(texto).then(() => {
      this.copiadoExitoso.set(true);
      setTimeout(() => this.copiadoExitoso.set(false), 2000);
    });
  }

  irANuevaEmision(): void {
    const adm = this.administradoSeleccionado();
    if (adm) {
      this.router.navigate(['/nueva'], {
        queryParams: {
          ruc: adm.ruc || '',
          dni: adm.nroDocumento || '',
          nombre: adm.nombreCompleto || adm.razonSocial || '',
          correo: adm.correoElectronico || ''
        }
      });
    } else {
      this.router.navigate(['/nueva']);
    }
  }

  abrirModalJson(): void {
    this.modalJsonAbierto.set(true);
  }

  cerrarModalJson(): void {
    this.modalJsonAbierto.set(false);
  }

  imprimirFicha(): void {
    window.print();
  }
}
