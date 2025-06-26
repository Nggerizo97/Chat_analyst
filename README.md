# Bot Analytics Dashboard

## 📋 Descripción

Este repositorio contiene un análisis completo del tiempo de uso del bot y los costos asociados, diseñado para mostrar a los clientes los datos reales del manejo del bot. El análisis incluye métricas detalladas de costos, distribución de canales, escalaciones a asesores y visualizaciones gráficas para presentaciones ejecutivas.

## 🎯 Métricas Clave Analizadas

### Costos Asociados
- **Costo por Interacción**: $75
- **Costo por Paso a Asesor**: $300  
- **Costo por Hora de Asesor**: $23,000
- **Promedio de Interacciones por Conversación**: 20 (objetivo)
- **Porcentaje de Conversaciones que Terminan con Asesor**: 30% (objetivo)
- **Tiempo Promedio de Atención del Asesor**: 5 a 10 minutos por conversación

### Canales Actuales
- **Disponibilidad**: Portal Web a través del widget y WhatsApp a través de la línea 3102205575
- **Distribución de Conversaciones**: 63% en WhatsApp, 37% en Portal Web (objetivo)

## 📁 Archivos del Proyecto

### Scripts de Análisis
1. **`bot_usage_analytics.py`** - Análisis principal enfocado en métricas específicas del negocio
2. **`bot_analytics.py`** - Análisis básico con visualizaciones estáticas
3. **`comprehensive_bot_analysis.py`** - Análisis avanzado con dashboard ejecutivo
4. **`dataconversacion1.ipynb`** - Notebook original de procesamiento de datos

### Datos de Entrada
- **`Conversación_2.json`** - Datos de conversaciones en formato JSON
- **`Excel_completo.xlsx`** - Datos procesados en Excel
- **`mi_archivo_excel.xlsx`** y **`mi_archivo_excel2.xlsx`** - Archivos de salida adicionales

## 🚀 Cómo Usar

### Prerrequisitos
```bash
pip install pandas matplotlib seaborn plotly openpyxl numpy
```

### Ejecutar Análisis Principal
```bash
python bot_usage_analytics.py
```

Este script genera:
- **Dashboard interactivo**: `client_bot_analytics_dashboard.html`
- **Reporte detallado**: Impreso en consola
- **Datos de resultados**: `bot_usage_analysis_YYYYMMDD_HHMMSS.json`

### Ejecutar Análisis Básico
```bash
python bot_analytics.py
```

Genera:
- **Dashboard estático**: `bot_analytics_dashboard.png`
- **Dashboard interactivo**: `interactive_bot_dashboard.html`

### Ejecutar Análisis Ejecutivo Completo
```bash
python comprehensive_bot_analysis.py
```

Genera:
- **Dashboard ejecutivo**: `executive_dashboard.html`
- **Métricas detalladas**: `comprehensive_bot_metrics.json`

## 📊 Resultados del Análisis Actual

### Resumen Ejecutivo
- **Total de Conversaciones Analizadas**: 18
- **Total de Interacciones de Usuario**: 151
- **Costo Operacional Total**: $68,475.00
- **Costo por Conversación**: $3,804.17

### Indicadores Clave de Rendimiento
- **Interacciones Promedio por Conversación**: 8.4 (Objetivo: 20) - 42% del objetivo
- **Tasa de Escalación a Asesor**: 100.0% (Objetivo: 30%) - Eficiencia: 30%
- **Distribución de Canales**: 100% Portal Web, 0% WhatsApp

### Análisis de Costos Detallado
- **Costos de Interacciones**: $11,325.00
- **Costos de Escalación a Asesor**: $5,400.00
- **Costos de Tiempo de Asesor**: $51,750.00
- **Horas Totales de Asesor**: 2.2 horas

## 📈 Visualizaciones Generadas

### Dashboard Principal (`client_bot_analytics_dashboard.html`)
1. **Interacciones por Conversación**: Comparación actual vs objetivo
2. **Tasa de Escalación a Asesor**: Actual vs objetivo
3. **Distribución de Canales**: Actual vs objetivo
4. **Desglose de Costos**: Por componente
5. **Tendencias Temporales**: Volumen y costos
6. **Métricas de Eficiencia**: Indicador de rendimiento
7. **Distribución de Satisfacción**: Calificaciones de clientes
8. **Duración de Conversaciones**: Análisis temporal
9. **KPIs Resumen**: Tabla de indicadores clave

### Otras Visualizaciones
- Dashboard estático (PNG)
- Dashboard ejecutivo interactivo
- Métricas de calidad y satisfacción

## 💡 Recomendaciones de Optimización

### Prioridad Alta
- **Reducir Tasa de Escalación**: La tasa actual (100%) está muy por encima del objetivo (30%)
- **Mejorar Base de Conocimiento**: Para reducir escalaciones y costos

### Prioridad Media
- **Optimizar Interacciones**: Aumentar de 8.4 a 20 interacciones promedio por conversación
- **Balancear Canales**: Aumentar uso de WhatsApp para alcanzar distribución objetivo

### Beneficios Potenciales
- **Ahorro de Costos**: Significativo mediante reducción de escalaciones
- **Mejor Experiencia de Usuario**: A través de conversaciones más completas
- **Optimización de Recursos**: Mejor distribución entre canales

## 🔧 Personalización

### Modificar Parámetros de Costo
Editar las constantes en cualquier script:
```python
BUSINESS_METRICS = {
    'cost_per_interaction': 75,
    'cost_per_advisor_step': 300,
    'cost_per_advisor_hour': 23000,
    'target_avg_interactions': 20,
    'target_advisor_percentage': 30,
    # ... otros parámetros
}
```

### Agregar Nuevos Datos
1. Actualizar `Conversación_2.json` con nuevas conversaciones
2. Actualizar `Excel_completo.xlsx` con datos procesados
3. Ejecutar cualquier script de análisis

## 📞 Soporte

Para preguntas sobre el análisis o personalizaciones adicionales, revisar:
- Comentarios en el código fuente
- Documentación inline en los scripts
- Resultados JSON generados para datos detallados

## 📋 Estructura de Datos

### Formato JSON de Conversaciones
```json
{
  "conversation_id": "string",
  "chatHistory": [
    {
      "datetime": "timestamp",
      "from": {"full_name": "string", "is_bot": boolean},
      "text": "string"
    }
  ],
  "channelId": "string",
  "datosParaAsesor": "object|null",
  "retroalimentacion": "number|null"
}
```

### Métricas Calculadas
- Interacciones por conversación
- Duración de conversaciones
- Tasa de escalación a asesor
- Distribución por canal
- Costos detallados por categoría
- Indicadores de eficiencia

---

**Nota**: Este análisis proporciona insights accionables para optimizar el rendimiento del bot y reducir costos operacionales mientras se mejora la experiencia del usuario.