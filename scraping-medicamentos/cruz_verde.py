

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def configurar_navegador():
    """Configura el navegador Chrome"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def buscar(driver, medicamento):
    """
    Función principal de búsqueda en Cruz Verde
    
    Args:
        driver: Instancia de WebDriver de Selenium
        medicamento: String con el nombre del medicamento a buscar
    
    Returns:
        dict: {'farmacia': str, 'nombre': str, 'precio': str} o None si no encuentra
    """
    try:
        driver.get("https://www.cruzverde.com.co/")
        time.sleep(6)
        
        search_box = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="Buscar"]')
        search_box.send_keys(medicamento)
        search_box.send_keys(Keys.ENTER)
        
        time.sleep(8)
        
        # Obtener TODAS las tarjetas de productos
        productos = driver.find_elements(By.CSS_SELECTOR, 'ml-card-product')
        
        if len(productos) > 1:
            # Seleccionar el SEGUNDO producto (índice 1)
            producto = productos[1]
            
            # Obtener nombre del segundo producto
            nombre = producto.find_element(By.CSS_SELECTOR, 'a[class*="font-open"] span.ng-star-inserted').text
            
            # Obtener precio del segundo producto
            precio = producto.find_element(By.CSS_SELECTOR, 'span.font-bold.text-prices').text
            
            return {
                'farmacia': 'Cruz Verde',
                'nombre': nombre,
                'precio': precio
            }
        elif len(productos) == 1:
            # Si solo hay un producto, usar el primero
            producto = productos[0]
            
            nombre = producto.find_element(By.CSS_SELECTOR, 'a[class*="font-open"] span.ng-star-inserted').text
            precio = producto.find_element(By.CSS_SELECTOR, 'span.font-bold.text-prices').text
            
            return {
                'farmacia': 'Cruz Verde',
                'nombre': nombre,
                'precio': precio
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error en Cruz Verde: {e}")
        return None

# EJECUCIÓN INDEPENDIENTE

if __name__ == "__main__":
    medicamento = input("¿Qué medicamento buscas?: ")
    driver = configurar_navegador()
    
    try:
        print("\nBuscando en Cruz Verde...")
        resultado = buscar(driver, medicamento)
        
        if resultado:
            print(f"\n Producto: {resultado['nombre']}")
            print(f" Precio: {resultado['precio']}")
        else:
            print("\n No se encontraron productos")
            
    except Exception as e:
        print(f"\n Error: {e}")
        
    finally:
        print("\nCerrando navegador...")
        time.sleep(2)
        driver.quit()
        print(" Proceso finalizado")