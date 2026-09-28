import { Injectable, signal, effect } from '@angular/core';

export type ThemeMode = 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  public currentTheme = signal<ThemeMode>('light');

  constructor() {
    // Detectar preferencia guardada en localStorage o del sistema
    const savedTheme = localStorage.getItem('govtech_theme') as ThemeMode;
    if (savedTheme) {
      this.setTheme(savedTheme);
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }

    // Efecto reactivo para actualizar clases HTML en documentElement
    effect(() => {
      const theme = this.currentTheme();
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
      }
      localStorage.setItem('govtech_theme', theme);
    });
  }

  public toggleTheme(): void {
    this.currentTheme.update(curr => (curr === 'light' ? 'dark' : 'light'));
  }

  public setTheme(mode: ThemeMode): void {
    this.currentTheme.set(mode);
  }
}
