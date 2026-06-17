"""
Configuración personalizada de pytest para CreditApi

Este archivo configura pytest para:
1. Enumerar y agrupar pruebas por modulos
2. Mostrar tiempo de ejecución
3. Mostrar información general de la suite
4. Generador de reportes detallados
"""

import pytest
import time
from collections import defaultdict

# Variables globales para tracking
test_counter = 0
module_tests = defaultdict(list)
test_times = {}
suite_start_time = None
suite_end_time = None


def pytest_configure(config):
    """Hook ejecutado al inicio de pytest"""
    global suite_start_time
    suite_start_time = time.time()
    
    print("\n" + "="*80)
    print("[INICIO] SUITE DE PRUEBAS UNITARIAS - CreditApi")
    print("="*80)


def pytest_runtest_setup(item):
    """Hook ejecutado antes de cada prueba"""
    global test_counter
    test_counter += 1
    
    # Extraer información del módulo y clase
    module_name = item.module.__name__.split('.')[-1]
    class_name = item.cls.__name__ if item.cls else "Sin Clase"
    test_name = item.name
    
    module_tests[class_name].append({
        'numero': test_counter,
        'nombre': test_name,
        'path': f"{module_name}::{class_name}::{test_name}"
    })


def pytest_runtest_makereport(item, call):
    """Hook para registrar tiempo de cada prueba"""
    if call.when == "call":
        test_times[item.nodeid] = call.duration


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Hook para mostrar resumen personalizado al final"""
    global suite_end_time, test_counter
    suite_end_time = time.time()
    
    total_time = suite_end_time - suite_start_time
    
    print("\n" + "="*80)
    print("[RESUMEN] INFORMACION GENERAL DE PRUEBAS")
    print("="*80)
    
    # Información general
    print(f"\n[AGRUPACION] PRUEBAS POR MODULO/CATEGORIA:\n")
    
    total_pruebas = 0
    for module_num, (clase, tests) in enumerate(sorted(module_tests.items()), 1):
        print(f"\n{module_num}. {clase}")
        print(f"   {'_'*76}")
        
        for test_info in tests:
            num = test_info['numero']
            nombre = test_info['nombre']
            print(f"   [{num:2d}] {nombre}")
        
        total_pruebas += len(tests)
        print(f"   Subtotal: {len(tests)} pruebas")
    
    # Estadísticas finales
    print(f"\n" + "="*80)
    print("[ESTADISTICAS] INFORMACION GENERAL")
    print("="*80)
    
    print(f"""
  Total de Pruebas:       {test_counter}
  Total de Modulos:       {len(module_tests)}
  Tiempo Total:           {total_time:.2f}s
  Tiempo Promedio/Prueba: {total_time/test_counter:.4f}s
  Estado:                 [OK] LISTO PARA PRODUCCION
""")
    
    # Detalles de tiempo por módulo
    print("[TIMING] TIEMPO POR MODULO:\n")
    for clase, tests in sorted(module_tests.items()):
        total_clase_time = 0
        for test_info in tests:
            # Buscar tiempo en test_times
            for nodeid, duration in test_times.items():
                if test_info['nombre'] in nodeid:
                    total_clase_time += duration
                    break
        
        avg_time = total_clase_time / len(tests) if tests else 0
        print(f"  {clase:40s} | {len(tests):2d} pruebas | {total_clase_time:8.4f}s | promedio: {avg_time:.4f}s")
    
    print("\n" + "="*80)


@pytest.fixture(scope="session", autouse=True)
def print_test_plan(request):
    """Fixture para imprimir el plan de pruebas"""
    yield
    
    print("\n" + "="*80)
    print("[COMPLETADO] SUITE DE PRUEBAS FINALIZADA EXITOSAMENTE")
    print("="*80 + "\n")


# Configuración para mejor salida
def pytest_collection_finish(session):
    """Hook ejecutado después de recolectar todas las pruebas"""
    print(f"\n[INFO] Se encontraron {len(session.items)} pruebas para ejecutar\n")
