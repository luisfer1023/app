
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
    Función principal de búsqueda en Pasteur
    
    Args:
        driver: Instancia de WebDriver de Selenium
        medicamento: String con el nombre del medicamento a buscar
    
    Returns:
        dict: {'farmacia': str, 'nombre': str, 'precio': str} o None si no encuentra
    """
    try:
        driver.get("https://www.farmaciaspasteur.com.co/")
        time.sleep(5)
        
        search_box = driver.find_element(By.CSS_SELECTOR, 'input#downshift-0-input')
        search_box.send_keys(medicamento)
        search_box.send_keys(Keys.ENTER)
        
        time.sleep(7)
        
        productos = driver.find_elements(By.CSS_SELECTOR, 'div.vtex-search-result-3-x-galleryItem')
        
        if len(productos) > 0:
            producto = productos[0]
            nombre = producto.find_element(By.CSS_SELECTOR, 'span.vtex-product-summary-2-x-productBrand').text
            precio = producto.find_element(By.CSS_SELECTOR, 'span.vtex-product-price-1-x-sellingPriceValue').text
            
            return {
                'farmacia': 'Pasteur',
                'nombre': nombre,
                'precio': precio
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error en Pasteur: {e}")
        return None

# EJECUCIÓN INDEPENDIENTE
if __name__ == "__main__":
    # Este bloque solo se ejecuta si corres: python pasteur.py
    # NO se ejecuta cuando lo importas desde buscador_simple.py
    
    medicamento = input("¿Qué medicamento buscas?: ")
    driver = configurar_navegador()
    
    try:
        print("\nBuscando en Pasteur...")
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