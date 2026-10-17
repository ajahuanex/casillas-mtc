import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    @if (authService.isLoginModalOpen()) {
      <div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md transition-all animate-fadeIn">
        
        <!-- Contenedor del Modal -->
        <div class="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden transform transition-all animate-scaleUp">
          
          <!-- Franja Soberana MTC / Perú -->
          <div class="h-1.5 w-full bg-gradient-to-r from-red-600 via-white to-blue-800"></div>

          <!-- Encabezado Institucional -->
          <div class="p-6 pb-4 bg-slate-50/80 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center p-1 shadow-xs">
                  <img src="/assets/logos/logo-mtc-peru.jpg" alt="MTC" class="h-6 w-auto object-contain">
                </div>
                <div>
                  <h3 class="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                    Autenticación de Operador
                  </h3>
                  <p class="text-[11px] text-slate-500 dark:text-slate-400">
                    Sistema de Casilla Electrónica MTC / DRTC Puno
                  </p>
                </div>
              </div>

              <!-- Botón Cerrar -->
              <button (click)="authService.closeLoginModal()"
                      class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-700 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <!-- Selector de Modo de Autenticación -->
            <div class="mt-4 grid grid-cols-2 p-1 bg-slate-200/70 dark:bg-slate-800/60 rounded-lg text-xs font-semibold">
              <button (click)="tabActivo.set('dnie')"
                      [class.bg-white]="tabActivo() === 'dnie'"
                      [class.dark:bg-slate-700]="tabActivo() === 'dnie'"
                      [class.text-blue-900]="tabActivo() === 'dnie'"
                      [class.dark:text-blue-300]="tabActivo() === 'dnie'"
                      [class.shadow-xs]="tabActivo() === 'dnie'"
                      class="py-1.5 rounded-md flex items-center justify-center gap-1.5 transition-all text-slate-600 dark:text-slate-400 cursor-pointer">
                <span class="material-symbols-outlined text-[16px]">badge</span>
                <span>DNIe / PKI</span>
              </button>
              <button (click)="tabActivo.set('clave')"
                      [class.bg-white]="tabActivo() === 'clave'"
                      [class.dark:bg-slate-700]="tabActivo() === 'clave'"
                      [class.text-blue-900]="tabActivo() === 'clave'"
                      [class.dark:text-blue-300]="tabActivo() === 'clave'"
                      [class.shadow-xs]="tabActivo() === 'clave'"
                      class="py-1.5 rounded-md flex items-center justify-center gap-1.5 transition-all text-slate-600 dark:text-slate-400 cursor-pointer">
                <span class="material-symbols-outlined text-[16px]">key</span>
                <span>Usuario / Clave</span>
              </button>
            </div>
          </div>

          <!-- Cuerpo del Formulario -->
          <div class="p-6 space-y-4">

            <!-- Modo 1: DNIe / Token PKI -->
            @if (tabActivo() === 'dnie') {
              <div class="space-y-4">
                <div class="p-3.5 bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/50 rounded-xl flex items-start gap-3">
                  <span class="material-symbols-outlined text-blue-700 dark:text-blue-400 text-[22px] shrink-0 mt-0.5">verified_user</span>
                  <div class="text-xs">
                    <div class="font-bold text-blue-900 dark:text-blue-200">Lector de Tarjetas Inteligentes DNIe</div>
                    <div class="text-[11px] text-blue-700 dark:text-blue-300 mt-0.5">
                      Inserte su DNI electrónico con chip o conecte su Token criptográfico del MTC / RENIEC.
                    </div>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1" for="dnie-cert">
                    Certificado Digital Detectado
                  </label>
                  <select id="dnie-cert" [(ngModel)]="dnieCert"
                          class="w-full text-xs font-mono-code px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-600 focus:outline-hidden">
                    <option value="01284920">01284920 - ING. V. MAMANI QUISPE (RENIEC AUT)</option>
                    <option value="40592811">40592811 - ABOG. C. MENDOZA PARI (DRTC PUNO)</option>
                    <option value="71829304">71829304 - LIC. J. FLORES MAMANI (OPERADOR MTC)</option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1" for="dnie-pin">
                    PIN de Seguridad DNIe (6 u 8 dígitos)
                  </label>
                  <input id="dnie-pin" type="password" [(ngModel)]="dniePin" placeholder="••••••••" maxlength="8"
                         class="w-full text-xs font-mono-code px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-600 focus:outline-hidden">
                </div>
              </div>
            } @else {
              <!-- Modo 2: Usuario y Contraseña Tradicional -->
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1" for="user-dni">
                    DNI / Documento del Operador
                  </label>
                  <input id="user-dni" type="text" [(ngModel)]="usuarioDni" placeholder="Ej. 01284920" maxlength="8"
                         class="w-full text-xs font-mono-code px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-600 focus:outline-hidden">
                </div>

                <div>
                  <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1" for="user-pass">
                    Contraseña Institucional
                  </label>
                  <input id="user-pass" type="password" [(ngModel)]="usuarioClave" placeholder="••••••••••••"
                         class="w-full text-xs px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-600 focus:outline-hidden">
                </div>

                <div>
                  <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1" for="user-rol">
                    Rol Operativo / Sede
                  </label>
                  <select id="user-rol" [(ngModel)]="usuarioRol"
                          class="w-full text-xs px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-600 focus:outline-hidden">
                    <option value="Operador Certificador">Operador Certificador - Notificaciones MTC</option>
                    <option value="Fiscalizador Legal">Fiscalizador Legal - Circulación Terrestre Puno</option>
                    <option value="Administrador">Administrador Regional DRTC Puno</option>
                  </select>
                </div>
              </div>
            }

            <!-- Telemetría de Seguridad y Registro de IP -->
            <div class="pt-2 border-t border-slate-200 dark:border-slate-700/60 flex items-center justify-between text-[11px] text-slate-500 font-mono-code">
              <span class="flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                {{ authService.clientIp() }}
              </span>
              <span>mTLS TLS 1.3</span>
            </div>

            <!-- Mensaje de Estado / Error si aplica -->
            @if (mensajeError()) {
              <div class="p-2.5 bg-rose-50 text-rose-800 border border-rose-200 rounded-lg text-xs flex items-center gap-2">
                <span class="material-symbols-outlined text-[16px] text-rose-600">error</span>
                <span>{{ mensajeError() }}</span>
              </div>
            }

            <!-- Botones de Acción -->
            <div class="pt-2 flex gap-2">
              <button (click)="authService.closeLoginModal()" type="button"
                      class="w-1/3 px-3 py-2 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                Cancelar
              </button>
              <button (click)="ejecutarLogin()" [disabled]="procesando()" type="button"
                      class="w-2/3 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 shadow-sm transition-all active:scale-[0.99] disabled:opacity-50"
                      style="color: #ffffff !important;">
                @if (procesando()) {
                  <span class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                } @else {
                  <span class="material-symbols-outlined text-[16px]">login</span>
                }
                <span style="color: #ffffff !important;">{{ procesando() ? 'Autenticando...' : 'Iniciar Sesión Segura' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    }
  `,
  styles: [`
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes scaleUp {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
    .animate-fadeIn { animation: fadeIn 0.2s ease-out; }
    .animate-scaleUp { animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1); }
  `]
})
export class LoginModalComponent {
  public authService = inject(AuthService);

  tabActivo = signal<'dnie' | 'clave'>('dnie');
  procesando = signal<boolean>(false);
  mensajeError = signal<string>('');

  dnieCert = '01284920';
  dniePin = '';

  usuarioDni = '01284920';
  usuarioClave = '';
  usuarioRol = 'Operador Certificador';

  ejecutarLogin(): void {
    this.procesando.set(true);
    this.mensajeError.set('');

    setTimeout(() => {
      this.procesando.set(false);

      if (this.tabActivo() === 'dnie') {
        const nombresMap: Record<string, string> = {
          '01284920': 'Ing. V. Mamani Quispe',
          '40592811': 'Abog. C. Mendoza Pari',
          '71829304': 'Lic. J. Flores Mamani'
        };
        const nombre = nombresMap[this.dnieCert] || 'Operador Autorizado MTC';
        this.authService.login(this.dnieCert, nombre, 'Operador Certificador', 'DNIe / PKI');
      } else {
        if (!this.usuarioDni || this.usuarioDni.length < 8) {
          this.mensajeError.set('Ingrese un número de DNI válido de 8 dígitos');
          return;
        }
        this.authService.login(this.usuarioDni, 'Operador ' + this.usuarioDni, this.usuarioRol, 'Contraseña Segura');
      }
    }, 700);
  }
}
