import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, of } from 'rxjs';

export interface OperadorUser {
  dni: string;
  nombre: string;
  cargo: string;
  entidad: string;
  rol: string;
  nodo: string;
  avatarInitials: string;
  autenticadoCon: 'DNIe / PKI' | 'Contraseña Segura';
  fechaSesion: string;
}

export interface ClientIpInfo {
  ip: string;
  display_ip: string;
  node: string;
  protocol: string;
  cipher: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);

  // Operador activo por defecto (GovTech DRTC Puno)
  private defaultUser: OperadorUser = {
    dni: '01284920',
    nombre: 'Ing. V. Mamani Quispe',
    cargo: 'Especialista en Fiscalización y Notificaciones',
    entidad: 'DRTC Puno / MTC',
    rol: 'Operador Certificador',
    nodo: 'Nodo Puno-Central (DRTC-01)',
    avatarInitials: 'VM',
    autenticadoCon: 'DNIe / PKI',
    fechaSesion: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
  };

  public currentUser = signal<OperadorUser | null>(this.getStoredUser() || this.defaultUser);
  public isLoggedIn = signal<boolean>(true);
  public isLoginModalOpen = signal<boolean>(false);

  // Telemetría de IP
  public clientIp = signal<string>('Detectando IP...');
  public clientIpNode = signal<string>('Nodo Puno-Central');
  public isSecureConnection = signal<boolean>(true);

  constructor() {
    this.detectClientIp();
  }

  public detectClientIp(): void {
    // 1. Intentar detectar desde backend local
    this.http.get<ClientIpInfo>('/api/v1/client-ip').pipe(
      catchError(() => {
        // Fallback a servicio público o dirección WAN oficial
        return of({
          ip: '190.119.245.18',
          display_ip: '190.119.245.18',
          node: 'Nodo Puno-Central (DRTC-01)',
          protocol: 'TLS 1.3 mTLS',
          cipher: 'ECDHE-RSA-AES256-GCM-SHA384'
        });
      })
    ).subscribe({
      next: (res) => {
        this.clientIp.set(res.display_ip || res.ip || '190.119.245.18');
        this.clientIpNode.set(res.node || 'Nodo Puno-Central');
      }
    });
  }

  public openLoginModal(): void {
    this.isLoginModalOpen.set(true);
  }

  public closeLoginModal(): void {
    this.isLoginModalOpen.set(false);
  }

  public login(dni: string, nombre: string, rol: string, tipoAuth: 'DNIe / PKI' | 'Contraseña Segura' = 'DNIe / PKI'): void {
    const initials = nombre.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
    const user: OperadorUser = {
      dni,
      nombre,
      cargo: rol === 'Administrador' ? 'Director de Circulación Terrestre' : 'Especialista Legal y Notificador',
      entidad: 'DRTC Puno / MTC',
      rol,
      nodo: 'Nodo Puno-Central (DRTC-01)',
      avatarInitials: initials || 'OP',
      autenticadoCon: tipoAuth,
      fechaSesion: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
    };

    this.currentUser.set(user);
    this.isLoggedIn.set(true);
    localStorage.setItem('casillas_mtc_user', JSON.stringify(user));
    this.closeLoginModal();
  }

  public logout(): void {
    this.currentUser.set(null);
    this.isLoggedIn.set(false);
    localStorage.removeItem('casillas_mtc_user');
  }

  private getStoredUser(): OperadorUser | null {
    try {
      const data = localStorage.getItem('casillas_mtc_user');
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  }
}
