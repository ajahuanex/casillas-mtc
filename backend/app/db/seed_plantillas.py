"""
Seed de Plantillas Oficiales de Notificaciones Telemáticas (MTC / DRTC Puno)
Codificación con prefijo 'P-' y fundamentación en la Ley 27444, D.S. 001-2020-MTC,
D.S. 017-2009-MTC (RNAT), D.S. 016-2009-MTC (Tránsito) y Ley 26979 (Coactiva).
"""

from typing import List, Dict, Any

PLANTILLAS_SEMILLA: List[Dict[str, Any]] = [
    # ==========================================
    # FAMILIA A: PROCEDIMIENTO SANCIONADOR (PAS)
    # ==========================================
    {
        "codigo": "P-PAS-01",
        "nombre": "Imputación de Cargos - Acta de Fiscalización RNAT",
        "categoria": "FISCALIZADORA",
        "tipo_procedimiento": "Procedimiento Administrativo Sancionador - Transporte Terrestre",
        "base_legal": "Art. 255 del TUO de la Ley N° 27444 y Arts. 94 al 118 del D.S. N° 017-2009-MTC (RNAT).",
        "asunto_predeterminado": "NOTIFICACIÓN DE INICIO DE PAS E IMPUTACIÓN DE CARGOS - ACTA DE FISCALIZACIÓN N° {{NUMERO_ACTA}}",
        "plazo_dias_defecto": 5,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_DOCUMENTO", "NUMERO_EXPEDIENTE", "NUMERO_ACTA",
            "FECHA_INTERVENCION", "LUGAR_INTERVENCION", "PLACA_RODAJE", "CODIGO_INFRACCION", "DESCRIPCION_CONDUCTA"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #00236f; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00236f;">DIRECCIÓN REGIONAL DE TRANSPORTES Y COMUNICACIONES - DRTC PUNO</h3>
        <h4 style="margin: 4px 0 0 0; color: #475569;">SUBDIRECCIÓN DE FISCALIZACIÓN Y CONTROL DEL TRANSPORTE</h4>
        <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: bold; color: #dc2626;">CÉDULA DE IMPUTACIÓN DE CARGOS - TRANSPORTE TERRESTRE</p>
    </div>

    <p><strong>EXPEDIENTE N°:</strong> {{NUMERO_EXPEDIENTE}}</p>
    <p><strong>DESTINATARIO:</strong> {{ADMINISTRADO_NOMBRE}} (DOC: {{NUMERO_DOCUMENTO}})</p>
    <p><strong>DOMICILIO TELEMÁTICO:</strong> Casilla Electrónica MTC N° {{CASILLA_MTC}}</p>

    <div style="background-color: #f8fafc; border-left: 4px solid #00236f; padding: 12px; margin: 15px 0;">
        <h4 style="margin-top: 0; color: #00236f;">I. HECHOS IMPUTADOS</h4>
        <p>Se hace de su conocimiento que con fecha <strong>{{FECHA_INTERVENCION}}</strong>, en el lugar <strong>{{LUGAR_INTERVENCION}}</strong>, inspectores de esta Dirección intervinieron el vehículo de placa de rodaje <strong>{{PLACA_RODAJE}}</strong>, levantándose el <strong>Acta de Fiscalización N° {{NUMERO_ACTA}}</strong> por la presunta comisión de la infracción tipificada con código <strong>{{CODIGO_INFRACCION}}</strong> del Reglamento Nacional de Administración de Transporte (D.S. N° 017-2009-MTC).</p>
        <p><strong>Conducta detectada:</strong> {{DESCRIPCION_CONDUCTA}}</p>
    </div>

    <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 12px; margin: 15px 0;">
        <h4 style="margin-top: 0; color: #dc2626;">II. DERECHO A DESCARGOS Y PLAZO PERENTORIO</h4>
        <p>Conforme al numeral 3 del Art. 255 del TUO de la Ley N° 27444, se le otorga el plazo improrrogable de <strong>CINCO (05) DÍAS HÁBILES</strong>, contados a partir del día hábil siguiente a la notificación válida del presente acto, para que presente sus descargos por escrito adjuntando los medios probatorios que considere pertinentes.</p>
        <p style="font-size: 12px; color: #64748b;"><em>Nota legal: De conformidad con el Art. 11 del D.S. N° 001-2020-MTC, el cómputo del plazo se iniciará al día hábil siguiente de la apertura voluntaria en su Casilla MTC o al vencer el quinto día hábil de gracia telemática (Ficción Legal).</em></p>
    </div>
</div>
        """
    },
    {
        "codigo": "P-PAS-02",
        "nombre": "Imputación de Cargos - Papeleta de Tránsito (PIT)",
        "categoria": "FISCALIZADORA",
        "tipo_procedimiento": "Procedimiento Sancionador de Tránsito Terrestre",
        "base_legal": "D.S. N° 016-2009-MTC (TUO del Reglamento Nacional de Tránsito - Código de Tránsito).",
        "asunto_predeterminado": "NOTIFICACIÓN DE PAPELETA DE INFRACCIÓN AL TRÁNSITO N° {{NUMERO_PAPELETA}} - PLACA {{PLACA_RODAJE}}",
        "plazo_dias_defecto": 5,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_DOCUMENTO", "NUMERO_EXPEDIENTE", "NUMERO_PAPELETA",
            "FECHA_INFRACCION", "PLACA_RODAJE", "CODIGO_INFRACCION_TRANSITO", "MONTO_MULTA_ESTIMADO"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #b91c1c; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #b91c1c;">SISTEMA DE GESTIÓN DE SANCIONES DE TRÁNSITO - MTC / DRTC</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: bold; color: #1e293b;">CÉDULA DE NOTIFICACIÓN DE PAPELETA DE INFRACCIÓN AL TRÁNSITO</p>
    </div>

    <p><strong>EXPEDIENTE:</strong> {{NUMERO_EXPEDIENTE}}</p>
    <p><strong>INFRACTOR / TITULAR:</strong> {{ADMINISTRADO_NOMBRE}} (DNI/RUC: {{NUMERO_DOCUMENTO}})</p>

    <p>Por medio de la presente, se le notifica formalmente la <strong>Papeleta de Infracción al Tránsito N° {{NUMERO_PAPELETA}}</strong>, impuesta en fecha <strong>{{FECHA_INFRACCION}}</strong> al vehículo de placa <strong>{{PLACA_RODAJE}}</strong>, tipificada bajo el código <strong>{{CODIGO_INFRACCION_TRANSITO}}</strong> del TUO del Reglamento Nacional de Tránsito.</p>

    <div style="background-color: #fffbeb; border: 1px solid #f59e0b; padding: 12px; border-radius: 6px; margin: 15px 0;">
        <h4 style="margin: 0 0 6px 0; color: #b45309;">Opciones del Administrado (Plazo: 5 Días Hábiles):</h4>
        <ul>
            <li><strong>Descargo:</strong> Presentar descargo formal ante la Mesa de Partes de la entidad en el plazo de 5 días hábiles.</li>
            <li><strong>Pronto Pago con Descuento:</strong> Acogerse al descuento de ley dentro del plazo establecido por la normativa vigente (Monto estimado: S/ {{MONTO_MULTA_ESTIMADO}}).</li>
        </ul>
    </div>
</div>
        """
    },
    {
        "codigo": "P-PAS-03",
        "nombre": "Notificación de Medida Cautelar / Preventiva en Transporte",
        "categoria": "FISCALIZADORA",
        "tipo_procedimiento": "Medida Cautelar Previa o de Carácter Provisional",
        "base_legal": "Art. 256 del TUO de la Ley N° 27444 y Art. 110 del D.S. N° 017-2009-MTC.",
        "asunto_predeterminado": "NOTIFICACIÓN DE MEDIDA PREVENTIVA / CAUTELAR - {{MEDIDA_CAUTELAR_TIPO}}",
        "plazo_dias_defecto": 3,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RESOLUCION_CAUTELAR",
            "MEDIDA_CAUTELAR_TIPO", "FUNDAMENTACION_PELIGRO", "PLACA_RODAJE"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #7c3aed; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #7c3aed;">DIRECCIÓN DE CIRCULACIÓN TERRESTRE - MEDIDA CAUTELAR</h3>
        <p style="margin: 4px 0 0 0; font-weight: bold; color: #dc2626;">EJECUCIÓN INMEDIATA CONFORME AL ART. 256 LEY N° 27444</p>
    </div>

    <p>Se pone en su conocimiento la <strong>Resolución de Medida Cautelar N° {{NUMERO_RESOLUCION_CAUTELAR}}</strong>, emitida en el marco del Expediente N° {{NUMERO_EXPEDIENTE}}, la cual dispone lo siguiente:</p>

    <div style="background-color: #f5f3ff; border-left: 4px solid #7c3aed; padding: 12px; margin: 15px 0;">
        <p><strong>MEDIDA DISPUESTA:</strong> {{MEDIDA_CAUTELAR_TIPO}}</p>
        <p><strong>UNIDAD AFECTADA:</strong> Placa {{PLACA_RODAJE}}</p>
        <p><strong>SUSTENTO DE URGENCIA Y RIESGO A LA SEGURIDAD VIAL:</strong> {{FUNDAMENTACION_PELIGRO}}</p>
    </div>

    <p>Se le otorga el plazo de <strong>TRES (03) DÍAS HÁBILES</strong> a efectos de que formule su oposición conforme a ley, sin que ello suspenda la eficacia ejecutoria inmediata de la medida preventiva.</p>
</div>
        """
    },
    {
        "codigo": "P-PAS-04",
        "nombre": "Notificación de Informe Final de Instrucción (IFI)",
        "categoria": "FISCALIZADORA",
        "tipo_procedimiento": "Conclusión de Fase Instructora PAS",
        "base_legal": "Numeral 5 del Art. 255 del TUO de la Ley N° 27444.",
        "asunto_predeterminado": "NOTIFICACIÓN DE INFORME FINAL DE INSTRUCCIÓN N° {{NUMERO_IFI}} - EXPEDIENTE N° {{NUMERO_EXPEDIENTE}}",
        "plazo_dias_defecto": 5,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_IFI", "PROPUESTA_SANCION", "MONTO_PROPUESTO_UIT"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #0284c7;">DIRECCIÓN DE FISCALIZACIÓN Y CONTROL DEL TRANSPORTE</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: bold;">TRASLADO DE INFORME FINAL DE INSTRUCCIÓN (ART. 255.5 LEY 27444)</p>
    </div>

    <p>Se pone en conocimiento del administrado <strong>{{ADMINISTRADO_NOMBRE}}</strong> el <strong>Informe Final de Instrucción N° {{NUMERO_IFI}}</strong>, emitido por el Órgano Instructor en el Expediente N° {{NUMERO_EXPEDIENTE}}.</p>

    <div style="background-color: #f0f9ff; border: 1px solid #bae6fd; padding: 12px; border-radius: 6px; margin: 15px 0;">
        <h4 style="margin: 0 0 6px 0; color: #0369a1;">Conclusiones del Órgano Instructor:</h4>
        <p>Se concluye la existencia de responsabilidad administrativa, proponiéndose la sanción de: <strong>{{PROPUESTA_SANCION}}</strong> (Equivalente a {{MONTO_PROPUESTO_UIT}} UIT).</p>
    </div>

    <p>De conformidad con el Art. 255.5 de la Ley N° 27444, se le otorga el plazo de <strong>CINCO (05) DÍAS HÁBILES</strong> para que formule sus alegatos finales ante el Órgano Decisor previo a la emisión de la Resolución Final.</p>
</div>
        """
    },
    {
        "codigo": "P-PAS-05",
        "nombre": "Resolución Directoral de Sanción (RDS)",
        "categoria": "FISCALIZADORA",
        "tipo_procedimiento": "Fase Sancionadora / Decisora PAS",
        "base_legal": "Art. 257 y 218 del TUO de la Ley N° 27444 y Art. 117 del D.S. N° 017-2009-MTC.",
        "asunto_predeterminado": "NOTIFICACIÓN DE RESOLUCIÓN DIRECTORAL DE SANCIÓN N° {{NUMERO_RDS}}",
        "plazo_dias_defecto": 15,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RDS", "SANCIÓN_DETALLE", "MONTO_SOLES", "INFRACCION_CONFIRMADA"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #b91c1c; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00236f;">GOBIERNO REGIONAL PUNO - DRTC</h3>
        <h4 style="margin: 4px 0 0 0; color: #b91c1c;">RESOLUCIÓN DIRECTORAL DE SANCIÓN N° {{NUMERO_RDS}}</h4>
    </div>

    <p><strong>ADMINISTRADO:</strong> {{ADMINISTRADO_NOMBRE}}</p>
    <p><strong>EXPEDIENTE:</strong> {{NUMERO_EXPEDIENTE}}</p>

    <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 12px; border-radius: 6px; margin: 15px 0;">
        <h4 style="margin: 0 0 6px 0; color: #991b1b;">PARTE RESOLUTIVA:</h4>
        <p><strong>ARTÍCULO PRIMERO.- SANCIONAR</strong> a {{ADMINISTRADO_NOMBRE}} por la infracción <strong>{{INFRACCION_CONFIRMADA}}</strong>, imponiéndose la sanción de: <strong>{{SANCIÓN_DETALLE}}</strong>, ascendente a la suma de <strong>S/ {{MONTO_SOLES}}</strong>.</p>
    </div>

    <p><strong>DERECHO DE IMPUGNACIÓN:</strong> Se le notifica que contra el presente acto proceden los recursos de <strong>Reconsideración</strong> o <strong>Apelación</strong> en el plazo perentorio de <strong>QUINCE (15) DÍAS HÁBILES</strong>, conforme al Art. 218 de la Ley N° 27444. Vencido dicho plazo sin impugnación, el acto quedará firme y expedito para su remisión a la Oficina de Ejecución Coactiva.</p>
</div>
        """
    },
    {
        "codigo": "P-PAS-06",
        "nombre": "Resolución de Archivo o Caducidad/Prescripción",
        "categoria": "FISCALIZADORA",
        "tipo_procedimiento": "Conclusión y Archivo del PAS",
        "base_legal": "Arts. 252 (Prescripción) y 259 (Caducidad) del TUO de la Ley N° 27444.",
        "asunto_predeterminado": "NOTIFICACIÓN DE RESOLUCIÓN DE ARCHIVO DEFINITIVO N° {{NUMERO_RESOLUCION_ARCHIVO}}",
        "plazo_dias_defecto": 0,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RESOLUCION_ARCHIVO", "CAUSAL_ARCHIVO"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #059669; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #059669;">RESOLUCIÓN DE ARCHIVO DEFINITIVO</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px;">DIRECCIÓN REGIONAL DE TRANSPORTES Y COMUNICACIONES</p>
    </div>

    <p>Se notifica a <strong>{{ADMINISTRADO_NOMBRE}}</strong> la <strong>Resolución N° {{NUMERO_RESOLUCION_ARCHIVO}}</strong> emitida en el Expediente N° {{NUMERO_EXPEDIENTE}}, la cual dispone el <strong>ARCHIVO DEFINITIVO</strong> de los actuados por la causal de: <strong>{{CAUSAL_ARCHIVO}}</strong>.</p>
    <p>El presente acto agota la instancia instructora/sancionadora en el presente procedimiento.</p>
</div>
        """
    },

    # ==========================================
    # FAMILIA B: ADMINISTRATIVAS ORDINARIAS
    # ==========================================
    {
        "codigo": "P-ADM-01",
        "nombre": "Concesión / Renovación de Autorización de Ruta",
        "categoria": "ADMINISTRATIVA",
        "tipo_procedimiento": "Procedimiento TUPA - Autorización de Transporte Interprovincial",
        "base_legal": "Arts. 48 al 56 del D.S. N° 017-2009-MTC (RNAT).",
        "asunto_predeterminado": "RESOLUCIÓN DIRECTORAL DE AUTORIZACIÓN DE RUTA N° {{NUMERO_RESOLUCION_RUTA}}",
        "plazo_dias_defecto": 15,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RESOLUCION_RUTA", "ORIGEN_RUTA", "DESTINO_RUTA", "VIGENCIA_ANIOS", "FLOTA_CANTIDAD"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #00236f; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00236f;">DIRECCIÓN DE CIRCULACIÓN TERRESTRE - DRTC PUNO</h3>
        <p style="margin: 4px 0 0 0; font-weight: bold; color: #0284c7;">OTORGAMIENTO / RENOVACIÓN DE AUTORIZACIÓN DE SERVICIO DE TRANSPORTE REGULAR</p>
    </div>

    <p>Se notifica a la empresa <strong>{{ADMINISTRADO_NOMBRE}}</strong> la aprobación de la autorización para prestar el servicio de transporte interprovincial de personas:</p>
    <ul>
        <li><strong>Ruta:</strong> {{ORIGEN_RUTA}} - {{DESTINO_RUTA}} (y viceversa).</li>
        <li><strong>Vigencia:</strong> {{VIGENCIA_ANIOS}} años a partir de la notificación efectiva.</li>
        <li><strong>Flota Autorizada:</strong> {{FLOTA_CANTIDAD}} unidades vehiculares operativas.</li>
    </ul>
    <p>Se le requiere apersonarse para el trámite de entrega de las Tarjetas Únicas de Circulación (TUC) electrónicas correspondientes.</p>
</div>
        """
    },
    {
        "codigo": "P-ADM-02",
        "nombre": "Habilitación Vehicular y Entrega de TUC",
        "categoria": "ADMINISTRATIVA",
        "tipo_procedimiento": "Habilitación de Vehículos para Servicio de Transporte",
        "base_legal": "Art. 64 del D.S. N° 017-2009-MTC.",
        "asunto_predeterminado": "CÉDULA DE ENTREGA DE TARJETA ÚNICA DE CIRCULACIÓN (TUC) - PLACA {{PLACA_RODAJE}}",
        "plazo_dias_defecto": 0,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "PLACA_RODAJE", "NUMERO_TUC", "FECHA_VENCIMIENTO_TUC"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #059669; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #059669;">TARJETA ÚNICA DE CIRCULACIÓN (TUC) ELECTRÓNICA</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px;">DIRECCIÓN DE CIRCULACIÓN TERRESTRE</p>
    </div>

    <p>Se pone en conocimiento de <strong>{{ADMINISTRADO_NOMBRE}}</strong> la emisión de la TUC electrónica para la unidad vehicular:</p>
    <div style="background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 12px; border-radius: 6px; margin: 15px 0;">
        <p><strong>PLACA DE RODAJE:</strong> {{PLACA_RODAJE}}</p>
        <p><strong>NÚMERO DE TUC:</strong> {{NUMERO_TUC}}</p>
        <p><strong>VIGENCIA HASTA:</strong> {{FECHA_VENCIMIENTO_TUC}}</p>
    </div>
    <p>La presente habilitación se encuentra acreditada en el Registro Nacional de Transporte Terrestre del MTC.</p>
</div>
        """
    },
    {
        "codigo": "P-ADM-03",
        "nombre": "Requerimiento de Subsanación Documentaria TUPA",
        "categoria": "ADMINISTRATIVA",
        "tipo_procedimiento": "Control Previo de Trámites TUPA",
        "base_legal": "Art. 136 del TUO de la Ley N° 27444.",
        "asunto_predeterminado": "REQUERIMIENTO DE SUBSANACIÓN DOCUMENTARIA - EXPEDIENTE N° {{NUMERO_EXPEDIENTE}}",
        "plazo_dias_defecto": 5,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "TRAMITE_SOLICITADO", "REQUISITOS_OBSERVADOS", "PLAZO_SUBSANACION_DIAS"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #d97706; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #d97706;">OBSERVACIÓN Y REQUERIMIENTO DE SUBSANACIÓN</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: bold;">ART. 136 LEY N° 27444</p>
    </div>

    <p>En el marco de su solicitud de <strong>{{TRAMITE_SOLICITADO}}</strong> (Expediente N° {{NUMERO_EXPEDIENTE}}), se ha verificado el incumplimiento de los siguientes requisitos formales:</p>
    <div style="background-color: #fffbeb; border: 1px solid #fde68a; padding: 12px; border-radius: 6px; margin: 15px 0;">
        <p><strong>REQUISITOS OBSERVADOS:</strong></p>
        <p>{{REQUISITOS_OBSERVADOS}}</p>
    </div>
    <p>Se le requiere subsanar las observaciones en el plazo perentorio de <strong>{{PLAZO_SUBSANACION_DIAS}} DÍAS HÁBILES</strong>, bajo apercibimiento de tenerse por no presentada su solicitud y archivarse el expediente.</p>
</div>
        """
    },
    {
        "codigo": "P-ADM-04",
        "nombre": "Modificación de Padrón de Flota Vehicular",
        "categoria": "ADMINISTRATIVA",
        "tipo_procedimiento": "Modificación de Flota (Incremento/Sustitución/Baja)",
        "base_legal": "Arts. 67 al 69 del D.S. N° 017-2009-MTC.",
        "asunto_predeterminado": "RESOLUCIÓN DE MODIFICACIÓN DE FLOTA VEHICULAR N° {{NUMERO_RESOLUCION_FLOTA}}",
        "plazo_dias_defecto": 15,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RESOLUCION_FLOTA", "TIPO_MODIFICACION_FLOTA", "PLACAS_AFECTADAS"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #00236f; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00236f;">DIRECCIÓN DE CIRCULACIÓN TERRESTRE</h3>
        <p style="margin: 4px 0 0 0; font-weight: bold;">MODIFICACIÓN DE REGISTRO DE FLOTA OPERATIVA</p>
    </div>

    <p>Se notifica a <strong>{{ADMINISTRADO_NOMBRE}}</strong> la aprobación de la modificación de flota vehicular ({{TIPO_MODIFICACION_FLOTA}}):</p>
    <p><strong>Unidades vehiculares:</strong> {{PLACAS_AFECTADAS}}</p>
    <p>Se actualiza el padrón oficial en el sistema de la DRTC Puno y en la base nacional del MTC.</p>
</div>
        """
    },
    {
        "codigo": "P-ADM-05",
        "nombre": "Solicitud de Desafiliación a la Empresa",
        "categoria": "ADMINISTRATIVA",
        "tipo_procedimiento": "Desafiliación Vehicular a Solicitud de Propietario",
        "base_legal": "Art. 70 del D.S. N° 017-2009-MTC.",
        "asunto_predeterminado": "NOTIFICACIÓN DE SOLICITUD DE DESAFILIACIÓN VEHICULAR - PLACA {{PLACA_RODAJE}}",
        "plazo_dias_defecto": 5,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "PROPIETARIO_NOMBRE", "PLACA_RODAJE"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #475569; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #00236f;">TRASLADO DE SOLICITUD DE DESAFILIACIÓN</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px;">ART. 70 D.S. N° 017-2009-MTC</p>
    </div>

    <p>Se traslada a la empresa <strong>{{ADMINISTRADO_NOMBRE}}</strong> la solicitud presentada por el señor(a) <strong>{{PROPIETARIO_NOMBRE}}</strong>, propietario del vehículo de placa <strong>{{PLACA_RODAJE}}</strong>, solicitando la desafiliación de dicha unidad de su flota autorizada.</p>
    <p>Se le otorga el plazo de <strong>CINCO (05) DÍAS HÁBILES</strong> a efectos de que exprese lo conveniente a su derecho o remita la constancia de desafiliación correspondiente.</p>
</div>
        """
    },

    # ==========================================
    # FAMILIA C: RECURSOS E IMPUGNACIONES
    # ==========================================
    {
        "codigo": "P-REC-01",
        "nombre": "Resolución de Recurso de Reconsideración",
        "categoria": "IMPUGNATORIA",
        "tipo_procedimiento": "Recurso Administrativo de Reconsideración",
        "base_legal": "Art. 219 del TUO de la Ley N° 27444.",
        "asunto_predeterminado": "NOTIFICACIÓN DE RESOLUCIÓN QUE RESUELVE RECURSO DE RECONSIDERACIÓN N° {{NUMERO_RESOLUCION_RECON}}",
        "plazo_dias_defecto": 15,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RESOLUCION_RECON", "SENTIDO_FALLO", "DETALLE_ARGUMENTO"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #1e3a8a;">DIRECCIÓN REGIONAL DE TRANSPORTES Y COMUNICACIONES</h3>
        <p style="margin: 4px 0 0 0; font-weight: bold;">RESOLUCIÓN DE RECURSO DE RECONSIDERACIÓN</p>
    </div>

    <p>Se notifica a <strong>{{ADMINISTRADO_NOMBRE}}</strong> la <strong>Resolución N° {{NUMERO_RESOLUCION_RECON}}</strong>, la cual resuelve declarar: <strong>{{SENTIDO_FALLO}}</strong> el recurso de reconsideración interpuesto en el Expediente N° {{NUMERO_EXPEDIENTE}}.</p>
    <p><strong>Fundamentación:</strong> {{DETALLE_ARGUMENTO}}</p>
    <p>Se le informa que contra este acto procede la interposición del recurso de <strong>Apelación</strong> dentro del plazo perentorio de <strong>QUINCE (15) DÍAS HÁBILES</strong> ante la Gerencia Regional correspondiente.</p>
</div>
        """
    },
    {
        "codigo": "P-REC-02",
        "nombre": "Declaración de Firmeza y Consentimiento",
        "categoria": "IMPUGNATORIA",
        "tipo_procedimiento": "Constancia de Acto Firme",
        "base_legal": "Art. 222 del TUO de la Ley N° 27444.",
        "asunto_predeterminado": "DECLARACIÓN DE FIRMEZA Y CONSENTIMIENTO DE RESOLUCIÓN N° {{NUMERO_RESOLUCION_SANCION}}",
        "plazo_dias_defecto": 0,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE", "NUMERO_RESOLUCION_SANCION", "FECHA_NOTIFICACION_ORIGINAL"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #334155; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #334155;">CONSTANCIA DE ACTO FIRME Y CONSENTIDO</h3>
        <p style="margin: 4px 0 0 0; font-size: 13px;">ART. 222 DE LA LEY N° 27444</p>
    </div>

    <p>Se certifica que la <strong>Resolución N° {{NUMERO_RESOLUCION_SANCION}}</strong>, válidamente notificada en fecha {{FECHA_NOTIFICACION_ORIGINAL}}, ha quedado <strong>FIRME Y CONSENTIDA</strong> al haber vencido en exceso el plazo de 15 días hábiles sin que el administrado <strong>{{ADMINISTRADO_NOMBRE}}</strong> haya formulado recurso impugnatorio alguno.</p>
    <p>En consecuencia, el acto adquiere calidad de título de ejecución y se dispone la remisión de los actuados al Ejecutor Coactivo para el cobro forzoso de la acreencia.</p>
</div>
        """
    },

    # ==========================================
    # FAMILIA D: EJECUCIÓN COACTIVA
    # ==========================================
    {
        "codigo": "P-COA-01",
        "nombre": "REC N° 01 Mandamiento de Pago Coactivo",
        "categoria": "COACTIVA",
        "tipo_procedimiento": "Procedimiento de Ejecución Coactiva",
        "base_legal": "Arts. 14 y 15 de la Ley N° 26979 (Ley de Procedimiento de Ejecución Coactiva).",
        "asunto_predeterminado": "RESOLUCIÓN DE EJECUCIÓN COACTIVA N° 01 - MANDAMIENTO DE PAGO DE DEUDA",
        "plazo_dias_defecto": 7,
        "tipo_plazo": "DIAS_HABILES",
        "variables_requeridas": [
            "ADMINISTRADO_NOMBRE", "NUMERO_EXPEDIENTE_COACTIVO", "NUMERO_RESOLUCION_DETERMINACION", "MONTO_DEUDA_TOTAL_SOLES", "DETALLE_CONCEPTO"
        ],
        "cuerpo_html_template": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
    <div style="text-align: center; border-bottom: 2px solid #b91c1c; padding-bottom: 12px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #b91c1c;">OFICINA DE EJECUCIÓN COACTIVA - DRTC PUNO</h3>
        <h4 style="margin: 4px 0 0 0; color: #00236f;">RESOLUCIÓN N° 01: MANDAMIENTO DE EJECUCIÓN COACTIVA</h4>
        <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: bold; color: #dc2626;">EXPEDIENTE COACTIVO N° {{NUMERO_EXPEDIENTE_COACTIVO}}</p>
    </div>

    <p><strong>OBLIGADO:</strong> {{ADMINISTRADO_NOMBRE}}</p>
    <p><strong>VALOR EXIGIBLE:</strong> Resolución Directoral N° {{NUMERO_RESOLUCION_DETERMINACION}}</p>
    <p><strong>MONTO DE LIQUIDACIÓN COACTIVA:</strong> <strong>S/ {{MONTO_DEUDA_TOTAL_SOLES}}</strong> (Concepto: {{DETALLE_CONCEPTO}}).</p>

    <div style="background-color: #fef2f2; border: 2px solid #b91c1c; padding: 14px; border-radius: 6px; margin: 15px 0;">
        <h4 style="margin-top: 0; color: #b91c1c;">INTIMACIÓN PERENTORIA DE PAGO (PLAZO: 7 DÍAS HÁBILES):</h4>
        <p>De conformidad con el Art. 15 de la Ley N° 26979, se le <strong>INTIMA</strong> a cancelar la totalidad de la deuda en el plazo perentorio de <strong>SIETE (07) DÍAS HÁBILES</strong> de notificada válidamente la presente resolución.</p>
        <p><strong>APERCIBIMIENTO:</strong> Vencido dicho plazo sin verificar el pago, se trabarán de inmediato <strong>MEDIDAS CAUTELARES DE EMBARGO</strong> en forma de retención de cuentas bancarias (mediante notificación a la SBS) y embargo en forma de <strong>secuestro e internamiento de vehículos</strong> ante la Policía Nacional del Perú.</p>
    </div>
</div>
        """
    }
]


async def sembrar_plantillas_si_no_existen(db_session):
    """Inserta o actualiza las plantillas oficiales con prefijo 'P-' en la base de datos."""
    from sqlalchemy import select
    from app.models.entities import PlantillaNotificacion

    for data in PLANTILLAS_SEMILLA:
        stmt = select(PlantillaNotificacion).where(PlantillaNotificacion.codigo == data["codigo"])
        result = await db_session.execute(stmt)
        plantilla = result.scalar_one_or_none()

        if not plantilla:
            nueva = PlantillaNotificacion(**data)
            db_session.add(nueva)
        else:
            # Actualizar campos clave para asegurar sincronización
            plantilla.nombre = data["nombre"]
            plantilla.categoria = data["categoria"]
            plantilla.tipo_procedimiento = data["tipo_procedimiento"]
            plantilla.base_legal = data["base_legal"]
            plantilla.asunto_predeterminado = data["asunto_predeterminado"]
            plantilla.plazo_dias_defecto = data["plazo_dias_defecto"]
            plantilla.tipo_plazo = data["tipo_plazo"]
            plantilla.cuerpo_html_template = data["cuerpo_html_template"]
            plantilla.variables_requeridas = data["variables_requeridas"]
            plantilla.activo = True

    await db_session.commit()
