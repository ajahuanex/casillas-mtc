---
name: verificacion-normativa-mtc
description: >-
  Verifica y asegura el estricto cumplimiento normativo peruano para notificaciones telemáticas
  en el Sistema de Casilla Electrónica MTC / DRTC según D.S. 001-2020-MTC, TUO Ley 27444 (LPAG),
  D.S. 017-2009-MTC (RNAT), D.S. 016-2009-MTC (Tránsito) y Ley 26979 (Ejecución Coactiva).
---

# Verificación de Cumplimiento Normativo MTC / DRTC

Esta skill gobierna la validez jurídica, el cómputo de plazos y el flujo de actos administrativos notificados telemáticamente.

## 1. Principio de Origen Oficial de Acuses (CAD y CAL)
- **CRÍTICO**: Los Acuses de Recibo / Depósito (**CAD**) y Acuses de Lectura / Acceso (**CAL**) **NO SE GENERAN LOCALMENTE**.
- Son emitidos y firmados digitalmente **únicamente por la API oficial del MTC** (`https://wscasilla.mtc.gob.pe/ms-notific/v2/servicios-publicos`).
- El backend debe invocar los endpoints de la API MTC para:
  1. Depositar la notificación (`/notificaciones/depositar` o equivalente).
  2. Recibir el `codigo_verificacion_mtc` oficial y el binario PDF del CAD.
  3. Consultar periódicamente o por webhook el estado de lectura para descargar el binario PDF del CAL emitido por el MTC.
  4. Custodiar los binarios originales del MTC en MinIO S3 con hash SHA-256 inmutable (WORM).

## 2. Reglas de Cómputo de Plazos Procesales (Art. 11 D.S. 001-2020-MTC)
1. **Periodo de Gracia para Apertura Voluntaria**:
   - Todo administrado cuenta con **cinco (5) días hábiles** desde la fecha de depósito en casilla para abrir voluntariamente el mensaje.
2. **Configuración de la Notificación Efectiva**:
   - **Caso A (Apertura voluntaria en ≤ 5 días hábiles)**: La notificación surte efectos el día y hora en que se genera el CAL en la API del MTC.
   - **Caso B (Ficción Legal Automática)**: Si transcurren los 5 días hábiles sin que el administrado abra la casilla, la notificación **se considera válidamente efectuada de pleno derecho al quinto (5°) día hábil**, consumándose la Ficción Legal (Art. 11 num. 11.2 D.S. 001-2020-MTC).
3. **Inicio del Cómputo del Plazo Sustantivo**:
   - El plazo para formular descargos o interponer recursos comienza a correr **a partir del día hábil siguiente** a aquel en que la notificación surtió efectos (ya sea por CAL voluntario o por Ficción Legal).
4. **Días Hábiles vs Calendario**:
   - Se excluyen sábados, domingos y feriados nacionales/regionales oficiales de la sede DRTC.

## 3. Codificación Oficial de Plantillas
Las plantillas oficiales de notificación deben iniciar obligatoriamente con el prefijo **`P-`**:
- Procedimientos Sancionadores: `P-PAS-01` a `P-PAS-06`
- Procedimientos Administrativos Ordinarios: `P-ADM-01` a `P-ADM-05`
- Recursos e Impugnaciones: `P-REC-01`, `P-REC-02`
- Procedimiento de Ejecución Coactiva: `P-COA-01`
