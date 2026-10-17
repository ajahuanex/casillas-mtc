---
name: angular22-architecture
description: >-
  Estándares de arquitectura, buenas prácticas y patrones de desarrollo para Angular 22+
  en el frontend del Sistema de Casilla Electrónica MTC / DRTC Puno.
---

# Estándares de Arquitectura Angular 22+

Esta skill define las pautas técnicas para el desarrollo en Angular 22+:

## 1. Versión Mínima y Paradigma Reactivo
- **Versión**: Angular 22.x como estándar base mínimo.
- **Signals First**:
  - Utilizar `signal()`, `computed()` y `effect()` para el estado local y reactivo.
  - Minimizar o prescindir del boilerplate RxJS complejo en componentes; reservar RxJS (`Observable`, `Subject`, `takeUntilDestroyed`) para flujos asíncronos HTTP e integración de eventos externos.
- **Standalone Components Exclusivos**:
  - Prohibido el uso de `NgModule`.
  - Todos los componentes, directivas y pipes deben declararse con `standalone: true`.
- **Estructura de Control de Flujo Moderna**:
  - Usar `@if`, `@else`, `@for`, `@switch` en lugar de directivas estructurales obsoletas `*ngIf`, `*ngFor`.
  - Aprovechar bloques `@defer (on viewport)` para componentes pesados (editores PDF, visores de constancias MTC).

## 2. Modo Oscuro y Estilizado Tailwind CSS
- **Regla Crítica de Contraste**:
  - Prohibido el uso de clases `dark:bg-surface-container` o equivalentes si están mapeadas a tokens claros.
  - Utilizar paleta explícita de alta fidelidad: `dark:bg-slate-900`, `dark:bg-slate-800`, `dark:border-slate-800`, `dark:text-slate-200`.
  - Los botones de acción crítica como "Nueva Emisión MTC" deben garantizar legibilidad con texto blanco forzado (`!text-white` / `#ffffff`).

## 3. Disposición de Menús y Pantalla
- Menú superior fijado en una sola fila (`h-14`), con elementos `shrink-0` y sin saltos de línea ni desbordamientos horizontales.
- Menú lateral izquierdo colapsable a barra de solo iconos (rail), persistiendo la preferencia en `localStorage`.
