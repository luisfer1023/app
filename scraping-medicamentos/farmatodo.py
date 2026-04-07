
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, urllib.parse


def configurar_navegador(headless=False):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def buscar_via_url(driver, termino):
    """
    Busca directamente usando la URL de búsqueda de Farmatodo.
    Extrae los productos de la página resultante.
    """
    try:
        termino_enc = urllib.parse.quote(termino)
        url = f"https://www.farmatodo.com.co/buscar?product={termino_enc}&departamento=Todos&filtros="
        print(" Navegando a:", url)
        driver.get(url)

        wait = WebDriverWait(driver, 15)
        # Esperar los elementos de producto
        productos = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.content-product"))
        )

        resultados = []
        for prod in productos:
            try:
                nombre = prod.find_element(By.CSS_SELECTOR, "p.text-title").text.strip()
            except:
                nombre = None
            try:
                marca = prod.find_element(By.CSS_SELECTOR, "p.text-brand").text.strip()
            except:
                marca = None
            try:
                precio = prod.find_element(By.CSS_SELECTOR, "span.price__text-price.price__full-price").text.strip()
            except:
                precio = None

            resultados.append({
                "farmacia": "Farmatodo",
                "marca": marca,
                "nombre": nombre,
                "precio": precio
            })

        return resultados

    except Exception as e:
        print(" Error al buscar vía URL:", e)
        return []


if __name__ == "__main__":
    termino = input("¿Qué medicamento buscas?: ").strip()
    driver = configurar_navegador(headless=False)
    try:
        resultados = buscar_via_url(driver, termino)
        if resultados:
            print(" Resultados encontrados:\n")
            for idx, item in enumerate(resultados, start=1):
                print(f"{idx}. {item['marca']} — {item['nombre']} — {item['precio']}")
        else:
            print(" No se encontraron resultados.")
    finally:
        print("\nCerrando navegador...")
        time.sleep(2)
        driver.quit()
        print(" Proceso finalizado")
