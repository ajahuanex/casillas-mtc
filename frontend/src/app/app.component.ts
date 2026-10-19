import { Component, signal, OnInit, OnDestroy, inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ThemeService } from './core/services/theme.service';
import { AuthService } from './core/services/auth.service';
import { PreloaderService } from './core/services/preloader.service';
import { CasillaService } from './core/services/casilla.service';
import { LoginModalComponent } from './core/components/login-modal/login-modal.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, LoginModalComponent],
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'casillas-frontend';
  public themeService = inject(ThemeService);
  public authService = inject(AuthService);
  public preloaderService = inject(PreloaderService);
  public casillaService = inject(CasillaService);

  horaActual = signal<string>('');
  isScrolled = signal<boolean>(false);
  isSidebarCollapsed = signal<boolean>(localStorage.getItem('casillas_sidebar_collapsed') === 'true');
  private intervalId: any;

  toggleSidebar(): void {
    const nuevoEstado = !this.isSidebarCollapsed();
    this.isSidebarCollapsed.set(nuevoEstado);
    localStorage.setItem('casillas_sidebar_collapsed', String(nuevoEstado));
  }

  @HostListener('window:scroll', [])
  onWindowScroll(): void {
    const scrollPos = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
    this.isScrolled.set(scrollPos > 30);
  }

  ngOnInit(): void {
    this.actualizarHora();
    this.intervalId = setInterval(() => this.actualizarHora(), 1000);
    this.onWindowScroll();
  }

  ngOnDestroy(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  private actualizarHora(): void {
    const ahora = new Date();
    const formato = new Intl.DateTimeFormat('es-PE', {
      timeZone: 'America/Lima',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
    this.horaActual.set(formato.format(ahora) + ' UTC-5');
  }
}
