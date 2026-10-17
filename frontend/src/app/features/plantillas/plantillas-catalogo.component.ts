import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { PlantillasService, Plantilla, PlantillaRenderResponse } from '../../core/services/plantillas.service';

@Component({
  selector: 'app-plantillas-catalogo',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="space-y-6">
      
      <!-- ENCABEZADO OFICIAL -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div class="flex items-center gap-2">
            <span class="h-6 w-1.5 bg-blue-700 rounded-xs"></span>
            <h1 class="text-xl md:text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Catálogo Oficial de Plantillas de Notificación
            </h1>
            <span class="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
              Prefijo P-* • Ley 27444
            </span>
          </div>
          <p class="text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Modelos estandarizados para actos administrativos y resoluciones fiscalizadoras en tránsito y transporte terrestre de la DRTC Puno.
          </p>
        </div>

        <div class="flex items-center gap-2">
          <a routerLink="/nueva"
             class="inline-flex items-center gap-1.5 bg-blue-700 hover:bg-blue-800 text-white px-4 py-2 rounded-xl text-xs font-semibold transition-all shadow-sm active:scale-[0.99] border border-blue-800/40"
             style="color: #ffffff !important;">
            <span class="material-symbols-outlined text-[18px]">add_circle</span>
            <span style="color: #ffffff !important;">Nueva Emisión MTC</span>
          </a>
        </div>
      </div>

      <!-- BARRA DE FILTROS POR CATEGORÍA Y BÚSQUEDA -->
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        <!-- Pestañas de Categoría -->
        <div class="flex flex-wrap items-center gap-1.5">
          <button (click)="categoriaActiva.set('TODAS')"
                  [class.bg-blue-700]="categoriaActiva() === 'TODAS'"
                  [class.text-white]="categoriaActiva() === 'TODAS'"
                  [class.dark:bg-blue-700]="categoriaActiva() === 'TODAS'"
                  [class.bg-slate-100]="categoriaActiva() !== 'TODAS'"
                  [class.dark:bg-slate-800]="categoriaActiva() !== 'TODAS'"
                  [class.text-slate-700]="categoriaActiva() !== 'TODAS'"
                  [class.dark:text-slate-300]="categoriaActiva() !== 'TODAS'"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer border border-transparent dark:border-slate-700">
            Todas ({{ plantillas().length }})
          </button>
          
          <button (click)="categoriaActiva.set('FISCALIZADORA')"
                  [class.bg-rose-700]="categoriaActiva() === 'FISCALIZADORA'"
                  [class.text-white]="categoriaActiva() === 'FISCALIZADORA'"
                  [class.bg-slate-100]="categoriaActiva() !== 'FISCALIZADORA'"
                  [class.dark:bg-slate-800]="categoriaActiva() !== 'FISCALIZADORA'"
                  [class.text-slate-700]="categoriaActiva() !== 'FISCALIZADORA'"
                  [class.dark:text-slate-300]="categoriaActiva() !== 'FISCALIZADORA'"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer border border-transparent dark:border-slate-700 flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            Fiscalizadoras / PAS
          </button>

          <button (click)="categoriaActiva.set('ADMINISTRATIVA')"
                  [class.bg-sky-700]="categoriaActiva() === 'ADMINISTRATIVA'"
                  [class.text-white]="categoriaActiva() === 'ADMINISTRATIVA'"
                  [class.bg-slate-100]="categoriaActiva() !== 'ADMINISTRATIVA'"
                  [class.dark:bg-slate-800]="categoriaActiva() !== 'ADMINISTRATIVA'"
                  [class.text-slate-700]="categoriaActiva() !== 'ADMINISTRATIVA'"
                  [class.dark:text-slate-300]="categoriaActiva() !== 'ADMINISTRATIVA'"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer border border-transparent dark:border-slate-700 flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-sky-500"></span>
            Administrativas Ordinarias
          </button>

          <button (click)="categoriaActiva.set('IMPUGNATORIA')"
                  [class.bg-indigo-700]="categoriaActiva() === 'IMPUGNATORIA'"
                  [class.text-white]="categoriaActiva() === 'IMPUGNATORIA'"
                  [class.bg-slate-100]="categoriaActiva() !== 'IMPUGNATORIA'"
                  [class.dark:bg-slate-800]="categoriaActiva() !== 'IMPUGNATORIA'"
                  [class.text-slate-700]="categoriaActiva() !== 'IMPUGNATORIA'"
                  [class.dark:text-slate-300]="categoriaActiva() !== 'IMPUGNATORIA'"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer border border-transparent dark:border-slate-700 flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
            Impugnatorias
          </button>

          <button (click)="categoriaActiva.set('COACTIVA')"
                  [class.bg-red-800]="categoriaActiva() === 'COACTIVA'"
                  [class.text-white]="categoriaActiva() === 'COACTIVA'"
                  [class.bg-slate-100]="categoriaActiva() !== 'COACTIVA'"
                  [class.dark:bg-slate-800]="categoriaActiva() !== 'COACTIVA'"
                  [class.text-slate-700]="categoriaActiva() !== 'COACTIVA'"
                  [class.dark:text-slate-300]="categoriaActiva() !== 'COACTIVA'"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer border border-transparent dark:border-slate-700 flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-red-600"></span>
            Coactivas (Ley 26979)
          </button>
        </div>

        <!-- Buscador por texto -->
        <div class="relative w-full md:w-64">
          <input [(ngModel)]="busquedaTexto"
                 type="text"
                 placeholder="Buscar por código P-*, nombre..."
                 class="w-full text-xs font-mono-code px-3 py-2 pl-9 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-blue-600 focus:outline-hidden">
          <span class="material-symbols-outlined text-[18px] text-slate-400 absolute left-2.5 top-2.5">
            search
          </span>
        </div>
      </div>

      <!-- GRILLA DE PLANTILLAS -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        @for (item of plantillasFiltradas(); track item.codigo) {
          <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group">
            
            <div>
              <!-- Cabecera de la Tarjeta con Badges -->
              <div class="flex items-start justify-between gap-2 mb-3">
                <span class="px-2.5 py-1 rounded-md text-xs font-mono-code font-bold bg-blue-50 dark:bg-blue-950/70 text-blue-900 dark:text-blue-300 border border-blue-200 dark:border-blue-800/80">
                  {{ item.codigo }}
                </span>

                <!-- Badge de Categoría -->
                @switch (item.categoria) {
                  @case ('FISCALIZADORA') {
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-900">
                      PAS / Sancionadora
                    </span>
                  }
                  @case ('ADMINISTRATIVA') {
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-50 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300 border border-sky-200 dark:border-sky-900">
                      Administrativa
                    </span>
                  }
                  @case ('IMPUGNATORIA') {
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900">
                      Impugnatoria
                    </span>
                  }
                  @case ('COACTIVA') {
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-50 dark:bg-red-950/60 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-900">
                      Ejecución Coactiva
                    </span>
                  }
                }
              </div>

              <!-- Título y Procedimiento -->
              <h3 class="text-sm font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                {{ item.nombre }}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                {{ item.tipo_procedimiento }}
              </p>

              <!-- Plazo Legal y Ficción Legal -->
              <div class="mt-4 p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-xs space-y-1">
                <div class="flex items-center justify-between">
                  <span class="text-slate-500 dark:text-slate-400">Plazo Legal:</span>
                  <span class="font-bold text-slate-800 dark:text-slate-200 font-mono-code">
                    @if (item.plazo_dias_defecto > 0) {
                      {{ item.plazo_dias_defecto }} DÍAS HÁBILES
                    } @else {
                      ACTO NOTIFICABLE
                    }
                  </span>
                </div>
                <div class="flex items-center justify-between text-[11px]">
                  <span class="text-slate-500 dark:text-slate-400">Gracia Telemática:</span>
                  <span class="text-emerald-700 dark:text-emerald-400 font-medium">5 días hábiles</span>
                </div>
              </div>

              <!-- Base Legal -->
              <div class="mt-3 text-[11px] text-slate-500 dark:text-slate-400">
                <span class="font-semibold text-slate-700 dark:text-slate-300">Base legal:</span> {{ item.base_legal }}
              </div>

              <!-- Tokens requeridos -->
              <div class="mt-3 flex flex-wrap gap-1">
                @for (token of item.variables_requeridas.slice(0, 4); track token) {
                  <span class="text-[10px] font-mono-code px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {{ token }}
                  </span>
                }
                @if (item.variables_requeridas.length > 4) {
                  <span class="text-[10px] font-mono-code px-1 py-0.2 text-slate-400">
                    +{{ item.variables_requeridas.length - 4 }} más
                  </span>
                }
              </div>
            </div>

            <!-- Botones de Acción -->
            <div class="mt-5 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
              <button (click)="abrirPrevisualizacion(item)"
                      class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer shadow-xs">
                <span class="material-symbols-outlined text-[16px]">visibility</span>
                <span>Previsualizar</span>
              </button>

              <button (click)="usarEnEmision(item)"
                      class="px-3 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer shadow-xs"
                      style="color: #ffffff !important;">
                <span class="material-symbols-outlined text-[16px]">draw</span>
                <span style="color: #ffffff !important;">Usar Plantilla</span>
              </button>
            </div>

          </div>
        }
      </div>

      <!-- MODAL DE PREVISUALIZACIÓN Y RENDERIZADO INTERACTIVO -->
      @if (plantillaModal(); as p) {
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 max-w-4xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            
            <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded font-mono-code font-bold text-xs bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300">
                    {{ p.codigo }}
                  </span>
                  <h3 class="text-base font-bold text-slate-900 dark:text-white">
                    {{ p.nombre }}
                  </h3>
                </div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {{ p.base_legal }}
                </p>
              </div>
              <button (click)="plantillaModal.set(null)" class="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 cursor-pointer">
                <span class="material-symbols-outlined text-[24px]">close</span>
              </button>
            </div>

            <!-- Previsualización de Cédula Renderizada -->
            <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                Asunto Predeterminado:
              </div>
              <div class="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-800 dark:text-slate-100 font-mono-code">
                {{ p.asunto_predeterminado }}
              </div>

              <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mt-4 mb-2">
                Estructura de la Cédula Telemática:
              </div>
              <div class="p-4 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-h-72 overflow-y-auto text-xs"
                   [innerHTML]="p.cuerpo_html_template">
              </div>
            </div>

            <!-- Footer del Modal -->
            <div class="flex items-center justify-between pt-3 border-t border-slate-200 dark:border-slate-800">
              <span class="text-xs font-mono-code text-slate-500">
                Plazo: {{ p.plazo_dias_defecto }} días • Ficción legal 5 días
              </span>
              <div class="flex items-center gap-2">
                <button (click)="plantillaModal.set(null)"
                        class="px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors cursor-pointer">
                  Cerrar
                </button>
                <button (click)="usarEnEmision(p)"
                        class="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-semibold transition-colors cursor-pointer shadow-xs"
                        style="color: #ffffff !important;">
                  Continuar con esta Plantilla
                </button>
              </div>
            </div>

          </div>
        </div>
      }

    </div>
  `
})
export class PlantillasCatalogoComponent implements OnInit {
  private plantillasService = inject(PlantillasService);
  private router = inject(Router);

  public plantillas = this.plantillasService.plantillas;
  public cargando = this.plantillasService.cargando;
  public categoriaActiva = signal<string>('TODAS');
  public busquedaTexto = signal<string>('');
  public plantillaModal = signal<Plantilla | null>(null);

  public plantillasFiltradas = computed(() => {
    let lista = this.plantillas();
    const cat = this.categoriaActiva();
    const q = this.busquedaTexto().toLowerCase().trim();

    if (cat !== 'TODAS') {
      lista = lista.filter(p => p.categoria === cat);
    }

    if (q) {
      lista = lista.filter(p =>
        p.codigo.toLowerCase().includes(q) ||
        p.nombre.toLowerCase().includes(q) ||
        p.base_legal.toLowerCase().includes(q)
      );
    }

    return lista;
  });

  ngOnInit(): void {
    this.plantillasService.obtenerPlantillas().subscribe();
  }

  abrirPrevisualizacion(plantilla: Plantilla): void {
    this.plantillaModal.set(plantilla);
  }

  usarEnEmision(plantilla: Plantilla): void {
    this.plantillaModal.set(null);
    this.plantillasService.plantillaSeleccionada.set(plantilla);
    this.router.navigate(['/nueva'], { queryParams: { plantilla: plantilla.codigo } });
  }
}
