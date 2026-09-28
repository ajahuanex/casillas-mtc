import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NotificacionesService } from '../../core/services/notificaciones.service';
import { ThemeService } from '../../core/services/theme.service';
import { Notificacion, DashboardKpis, VerificarCasillaResponse } from '../../core/models/notificacion.model';

@Component({
  selector: 'app-dashboard-alertas',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard-alertas.component.html'
})
export class DashboardAlertasComponent implements OnInit {
  private notifService = inject(NotificacionesService);
  public themeService = inject(ThemeService);

  // Signals reactivos para el dashboard
  public kpis = signal<DashboardKpis>({
    total_notificaciones: 0,
    en_plazo_ordinario: 0,
    alerta_por_vencer_48h: 0,
    plazo_vencido: 0,
    notificadas_ficcion_legal: 0,
    en_gracia_lectura: 0
  });

  public notificaciones = signal<Notificacion[]>([]);
  public cargando = signal<boolean>(false);
  public error = signal<string | null>(null);

  // Filtros interactivos
  public filtroActivo = signal<string>('TODOS');
  public busquedaTexto = signal<string>('');

  // Verificación rápida de RUC / DNI
  public rucConsulta = signal<string>('20448192031');
  public verificandoRuc = signal<boolean>(false);
  public resultadoVerificacion = signal<VerificarCasillaResponse | null>(null);
  public errorVerificacion = signal<string | null>(null);

  // Modal de Hoja de Cómputo Legal
  public expedienteSeleccionado = signal<Notificacion | null>(null);

  // Lista filtrada computada
  public notificacionesFiltradas = computed(() => {
    let lista = this.notificaciones();
    const filtro = this.filtroActivo();
    const q = this.busquedaTexto().toLowerCase().trim();

    if (filtro === 'EN_PLAZO') {
      lista = lista.filter(n => n.estado_plazo === 'EN_PLAZO');
    } else if (filtro === 'ALERTA_48H') {
      lista = lista.filter(n => n.estado_plazo === 'POR_VENCER_48H' || n.estado_plazo === 'VENCE_HOY');
    } else if (filtro === 'VENCIDOS') {
      lista = lista.filter(n => n.estado_plazo === 'PLAZO_FENECIDO');
    } else if (filtro === 'FICCION_LEGAL') {
      lista = lista.filter(n => n.origen_notificacion_efectiva === 'FICCION_LEGAL_5_DIAS' || n.origen_notificacion_efectiva === 'FICCION_LEGAL_CONSUMADA');
    } else if (filtro === 'GRACIA') {
      lista = lista.filter(n => n.estado_plazo === 'EN_GRACIA_LECTURA');
    }

    if (q) {
      lista = lista.filter(n => 
        n.codigo_expediente.toLowerCase().includes(q) ||
        n.numero_acto_administrativo.toLowerCase().includes(q) ||
        n.asunto.toLowerCase().includes(q) ||
        (n.casilla?.codigo_casilla && n.casilla.codigo_casilla.toLowerCase().includes(q))
      );
    }

    return lista;
  });

  ngOnInit(): void {
    this.cargarDashboard();
    // Consulta inicial rápida de ejemplo
    this.consultarCasillaMTC();
  }

  public cargarDashboard(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.notifService.obtenerDashboardAlertas().subscribe({
      next: (resp) => {
        this.kpis.set(resp.kpis);
        this.notificaciones.set(resp.notificaciones);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error al conectar con la API de alertas MTC');
        this.cargando.set(false);
      }
    });
  }

  public consultarCasillaMTC(): void {
    const doc = this.rucConsulta().trim();
    if (!doc || doc.length < 8) {
      this.errorVerificacion.set('Ingrese un RUC (11 dígitos) o DNI (8 dígitos) válido.');
      return;
    }

    this.verificandoRuc.set(true);
    this.errorVerificacion.set(null);

    this.notifService.verificarCasilla(doc).subscribe({
      next: (res) => {
        this.resultadoVerificacion.set(res);
        this.verificandoRuc.set(false);
      },
      error: (err) => {
        this.errorVerificacion.set('No se pudo verificar la casilla en MTC.');
        this.verificandoRuc.set(false);
      }
    });
  }

  public setFiltro(filtro: string): void {
    this.filtroActivo.set(filtro);
  }

  public abrirModalComputo(notif: Notificacion): void {
    this.expedienteSeleccionado.set(notif);
  }

  public cerrarModalComputo(): void {
    this.expedienteSeleccionado.set(null);
  }

  public sincronizarConstancia(notif: Notificacion): void {
    this.notifService.sincronizarConstancias(notif.id).subscribe({
      next: () => {
        this.cargarDashboard();
      },
      error: (err) => {
        alert('Error al consultar constancias en MTC: ' + err.message);
      }
    });
  }

  public toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}
