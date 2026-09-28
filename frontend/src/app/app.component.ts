import { Component, signal, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ThemeService } from './core/services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'casillas-frontend';
  public themeService = inject(ThemeService);
  horaActual = signal<string>('');
  private intervalId: any;

  ngOnInit(): void {
    this.actualizarHora();
    this.intervalId = setInterval(() => this.actualizarHora(), 1000);
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
