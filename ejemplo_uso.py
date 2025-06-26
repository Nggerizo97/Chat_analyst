#!/usr/bin/env python3
"""
Ejemplo de Uso - Bot Analytics
=============================

Este script demuestra cómo ejecutar el análisis completo del bot
para generar reportes y dashboards para presentaciones a clientes.
"""

import os
import sys
from datetime import datetime

def main():
    """Ejecutar análisis completo del bot."""
    print("🤖 ANÁLISIS DE USO DEL BOT - EJEMPLO DE EJECUCIÓN")
    print("=" * 60)
    
    # Verificar archivos necesarios
    required_files = ['Conversación_2.json', 'Excel_completo.xlsx']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        print("Por favor, asegúrese de tener los archivos de datos necesarios.")
        return False
    
    print("✅ Archivos de datos encontrados")
    
    # Ejecutar análisis principal
    print("\n📊 Ejecutando análisis principal...")
    try:
        from bot_usage_analytics import BotUsageAnalytics
        
        analyzer = BotUsageAnalytics()
        results = analyzer.run_complete_analysis()
        
        if results:
            print("\n🎉 ¡Análisis completado exitosamente!")
            print("\n📁 Archivos generados:")
            
            generated_files = [
                'client_bot_analytics_dashboard.html',
                'bot_analytics_dashboard.png',
                'interactive_bot_dashboard.html'
            ]
            
            for file in generated_files:
                if os.path.exists(file):
                    size = os.path.getsize(file) / 1024  # KB
                    print(f"   ✅ {file} ({size:.1f} KB)")
                else:
                    print(f"   ❌ {file} (no generado)")
            
            # Mostrar resumen de métricas clave
            print("\n📈 RESUMEN EJECUTIVO:")
            print(f"   📞 Total de Conversaciones: {results.get('total_conversations', 0):,}")
            print(f"   💬 Total de Interacciones: {results.get('total_interactions', 0):,}")
            print(f"   💰 Costo Total: ${results.get('costs', {}).get('total_costs', 0):,.2f}")
            print(f"   📊 Costo por Conversación: ${results.get('costs', {}).get('cost_per_conversation', 0):.2f}")
            print(f"   🔄 Tasa de Escalación: {results.get('advisor_escalation_rate', 0):.1f}%")
            
            print("\n🌐 Para ver los resultados:")
            print("   1. Abrir 'client_bot_analytics_dashboard.html' en un navegador")
            print("   2. Revisar 'bot_analytics_dashboard.png' para vista estática")
            print("   3. Ver reporte detallado en la consola arriba")
            
            return True
            
        else:
            print("❌ Error en el análisis")
            return False
            
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Instalar dependencias: pip install pandas matplotlib seaborn plotly openpyxl")
        return False
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        return False

def show_usage_instructions():
    """Mostrar instrucciones de uso."""
    print("\n📖 INSTRUCCIONES DE USO:")
    print("-" * 40)
    print("1. Asegúrese de tener los archivos de datos:")
    print("   - Conversación_2.json")
    print("   - Excel_completo.xlsx")
    print("\n2. Instale las dependencias:")
    print("   pip install pandas matplotlib seaborn plotly openpyxl")
    print("\n3. Ejecute el análisis:")
    print("   python ejemplo_uso.py")
    print("\n4. Revise los archivos generados:")
    print("   - client_bot_analytics_dashboard.html (Dashboard principal)")
    print("   - bot_analytics_dashboard.png (Visualización estática)")
    print("   - interactive_bot_dashboard.html (Dashboard interactivo)")

if __name__ == "__main__":
    print(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_usage_instructions()
    else:
        success = main()
        
        if not success:
            print("\n❓ Para más información, ejecute:")
            print("   python ejemplo_uso.py --help")
    
    print(f"\nFinalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")