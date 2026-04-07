
import importlib
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def configurar_navegador():
    """Configura y retorna el navegador"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def extraer_precio_numerico(texto_precio):
    """Convierte el texto del precio a numero para ordenar"""
    if not texto_precio or texto_precio == "Sin precio" or texto_precio is None:
        return float('inf')
    
    # Eliminar todo excepto digitos, puntos y comas
    numeros = re.sub(r'[^\d,.]', '', str(texto_precio))
    # Reemplazar separadores de miles y decimales colombianos
    numeros = numeros.replace('.', '').replace(',', '.')
    
    try:
        return float(numeros)
    except:
        return float('inf')

#def buscar_en_cafam(driver, medicamento):
    """
    Cafam no tiene funcion buscar, solo extrae de URL directa
    Retornamos None porque no podemos buscar sin URL especifica
    """
    print("   CAFAM requiere URL directa del producto (no implementado para busqueda)")
    return None

def buscar_en_farmatodo(driver, medicamento):
    """
    Farmatodo usa buscar_via_url en lugar de buscar
    """
    try:
        import farmatodo
        resultados = farmatodo.buscar_via_url(driver, medicamento)
        
        if resultados and len(resultados) > 0:
            # Retornar el primer resultado en formato estandar
            primer_resultado = resultados[0]
            nombre_completo = f"{primer_resultado.get('marca', '')} {primer_resultado.get('nombre', '')}".strip()
            
            return {
                'farmacia': 'Farmatodo',
                'nombre': nombre_completo,
                'precio': primer_resultado.get('precio', 'Sin precio')
            }
        return None
    except Exception as e:
        print(f"   Error en Farmatodo: {str(e)[:80]}")
        return None

#def buscar_en_colsubsidio(driver, medicamento):
    """
    Colsubsidio esta vacio, retornamos None
    """
    print("   COLSUBSIDIO: Archivo vacio (no implementado)")
    return None

# PROGRAMA PRINCIPAL

print("\n" + "="*60)
print("       BUSCADOR DE PRECIOS DE MEDICAMENTOS")
print("="*60)

# Solicitar el medicamento
medicamento = input("\nQue medicamento deseas buscar?: ")

# Configurar navegador (compartido para todas las farmacias)
print("\nConfigurando navegador...")
driver = configurar_navegador()

# Lista de modulos de farmacias con configuracion especial para cada una
farmacias = [
    {
        'modulo': 'la_rebaja', 
        'funcion': 'buscar', 
        'nombre': 'La Rebaja Virtual',
        'especial': False
    },
    {
        'modulo': 'pasteur', 
        'funcion': 'buscar', 
        'nombre': 'Pasteur',
        'especial': False
    },
    {
        'modulo': 'cruz_verde', 
        'funcion': 'buscar', 
        'nombre': 'Cruz Verde',
        'especial': False
    },
    {
        'modulo': 'farmatodo', 
        'funcion': 'buscar_en_farmatodo',  # Funcion especial
        'nombre': 'Farmatodo',
        'especial': True
    },
    {
        'modulo': 'cafam', 
        'funcion': 'buscar_en_cafam',  # Funcion especial
        'nombre': 'Cafam',
        'especial': True
    },
    {
        'modulo': 'colsubsidio', 
        'funcion': 'buscar_en_colsubsidio',  # Funcion especial
        'nombre': 'Colsubsidio',
        'especial': True
    }
]

resultados = []

try:
    for farmacia in farmacias:
        print("\n" + "="*50)
        print(f"Buscando en {farmacia['nombre'].upper()}")
        print("="*50)
        
        try:
            resultado = None
            
            # Si es una farmacia especial, usar la funcion local
            if farmacia['especial']:
                if farmacia['funcion'] == 'buscar_en_farmatodo':
                    resultado = buscar_en_farmatodo(driver, medicamento)
                #elif farmacia['funcion'] == 'buscar_en_cafam':
                   # resultado = buscar_en_cafam(driver, medicamento)
                #elif farmacia['funcion'] == 'buscar_en_colsubsidio':
                    #resultado = buscar_en_colsubsidio(driver, medicamento)
            else:
                # Importar el modulo dinamicamente
                modulo = importlib.import_module(farmacia['modulo'])
                
                # Ejecutar la funcion buscar() del modulo
                if hasattr(modulo, farmacia['funcion']):
                    funcion_buscar = getattr(modulo, farmacia['funcion'])
                    resultado = funcion_buscar(driver, medicamento)
                else:
                    print(f"   El modulo {farmacia['modulo']} no tiene funcion '{farmacia['funcion']}'")
            
            # Procesar resultado
            if resultado:
                resultados.append(resultado)
                print(f"   Encontrado: {resultado['nombre']}")
                print(f"   Precio: {resultado['precio']}")
            else:
                print(f"   No se encontro en {farmacia['nombre']}")
                
        except ModuleNotFoundError:
            print(f"   Archivo {farmacia['modulo']}.py no encontrado")
        except Exception as e:
            print(f"   Error en {farmacia['nombre']}: {str(e)[:100]}")
        
        # Pausa entre busquedas
        time.sleep(2)

finally:
    # Cerrar navegador
    print("\n" + "="*60)
    print("Cerrando navegador...")
    driver.quit()
    print("Navegador cerrado")

# PROCESAR Y MOSTRAR RESULTADOS

# Agregar precio numerico para ordenar
for resultado in resultados:
    resultado['precio_numerico'] = extraer_precio_numerico(resultado['precio'])

# Ordenar de MENOR a MAYOR precio
resultados.sort(key=lambda x: x['precio_numerico'])

# Mostrar resultados
print("\n" + "="*60)
print("           RESULTADOS ORDENADOS POR PRECIO")
print("           (De menor a mayor)")
print("="*60)

if len(resultados) > 0:
    for i, r in enumerate(resultados, 1):
        print(f"\n{i}. {r['farmacia'].upper()}")
        print(f"   Producto: {r['nombre']}")
        print(f"   Precio: {r['precio']}")
        print("   " + "-"*55)
    
    # Filtrar solo los que tienen precio valido
    con_precio = [r for r in resultados if r['precio_numerico'] != float('inf')]
    
    print(f"\n{'='*60}")
    print(f"Total farmacias consultadas: {len(farmacias)}")
    print(f"Farmacias con resultados: {len(resultados)}")
    print(f"Farmacias con precio disponible: {len(con_precio)}")
    
    if con_precio:
        print(f"\nMEJOR PRECIO: {con_precio[0]['farmacia']} - {con_precio[0]['precio']}")
        
        if len(con_precio) > 1:
            ahorro = con_precio[-1]['precio_numerico'] - con_precio[0]['precio_numerico']
            porcentaje = (ahorro / con_precio[-1]['precio_numerico']) * 100
            print(f"Ahorras: ${ahorro:,.0f} COP ({porcentaje:.1f}%) vs la mas cara".replace(",", "."))
    
    print("="*60 + "\n")
    
    # EXPORTAR RESULTADOS A ARCHIVO
    try:
        with open('resultados_medicamentos.txt', 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RESULTADOS DE BUSQUEDA DE MEDICAMENTOS\n")
            f.write(f"Medicamento buscado: {medicamento}\n")
            f.write("="*60 + "\n\n")
            
            for i, r in enumerate(resultados, 1):
                f.write(f"{i}. {r['farmacia'].upper()}\n")
                f.write(f"   Producto: {r['nombre']}\n")
                f.write(f"   Precio: {r['precio']}\n")
                f.write("   " + "-"*55 + "\n\n")
            
            if con_precio:
                f.write("\n" + "="*60 + "\n")
                f.write(f"MEJOR PRECIO: {con_precio[0]['farmacia']} - {con_precio[0]['precio']}\n")
                f.write("="*60 + "\n")
        
        print("Resultados guardados en: resultados_medicamentos.txt\n")
    except Exception as e:
        print(f"No se pudo guardar el archivo: {e}\n")
        
else:
    print("\nNo se encontraron resultados en ninguna farmacia")
    print("="*60 + "\n")
    print("SUGERENCIAS:")
    print("- Verifica que el nombre del medicamento este escrito correctamente")
    print("- Intenta con el nombre generico del medicamento")
    print("- Verifica tu conexion a internet")
    print("="*60 + "\n")