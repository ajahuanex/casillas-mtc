import { Injectable, signal, inject } from '@angular/core';
import { Router, NavigationStart, NavigationEnd, NavigationCancel, NavigationError } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class PreloaderService {
  private router = inject(Router);

  public isLoading = signal<boolean>(false);
  public progress = signal<number>(0);
  private timer: any;

  constructor() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        this.startLoading();
      } else if (
        event instanceof NavigationEnd ||
        event instanceof NavigationCancel ||
        event instanceof NavigationError
      ) {
        this.completeLoading();
      }
    });
  }

  public startLoading(): void {
    this.isLoading.set(true);
    this.progress.set(15);

    if (this.timer) clearInterval(this.timer);

    this.timer = setInterval(() => {
      this.progress.update(p => {
        if (p < 80) return p + Math.floor(Math.random() * 15) + 5;
        if (p < 95) return p + 2;
        return p;
      });
    }, 120);
  }

  public completeLoading(): void {
    if (this.timer) clearInterval(this.timer);
    this.progress.set(100);

    setTimeout(() => {
      this.isLoading.set(false);
      this.progress.set(0);
    }, 280);
  }
}
