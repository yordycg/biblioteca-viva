#!/usr/bin/env python3
"""Prueba end-to-end del flujo principal con Selenium (F1, F2, F3).

Recorre en un navegador real: login del solicitante, busqueda, reserva, QR,
validacion de la entrega por el bibliotecario y registro de la devolucion.
Deja una captura por paso en docs/evidence/e2e/ y falla si algun paso no
coincide con lo esperado.

Requisitos:
    - Servidor en marcha con DEMO_MODE=1 para no depender de la hora real:
      DEMO_MODE=1 DEMO_NOW=2026-11-21T10:30:00 python manage.py runserver 127.0.0.1:8001
    - Selenium y un Chromium disponibles (Selenium Manager los resuelve solo).

Uso:
    .venv/bin/python scripts/prueba_e2e.py [URL] [fecha] [bloque]
"""
import os
import re
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001").rstrip("/")
FECHA = sys.argv[2] if len(sys.argv) > 2 else "2026-11-21"
BLOQUE = sys.argv[3] if len(sys.argv) > 3 else "11:00-12:00"
SALIDA = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "e2e"
CLAVE = "demo1234"
ESPERA = 15

pasos = []


def navegador():
    opciones = Options()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1280,900")
    return webdriver.Chrome(options=opciones)


def captura(driver, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(SALIDA / f"{nombre}.png"))


def comprobar(nombre, condicion, detalle=""):
    pasos.append((nombre, bool(condicion), detalle))
    print(f"{'OK ' if condicion else 'FALLA'}  {nombre}" + (f"  ({detalle})" if detalle else ""))
    if not condicion:
        raise AssertionError(nombre)


def entrar(driver, correo, destino="/buscar/"):
    driver.get(BASE + "/login/")
    driver.find_element(By.NAME, "username").send_keys(correo)
    driver.find_element(By.NAME, "password").send_keys(CLAVE)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    WebDriverWait(driver, ESPERA).until(EC.url_contains(destino))


def clic(driver, xpath):
    elemento = WebDriverWait(driver, ESPERA).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
    try:
        WebDriverWait(driver, ESPERA).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
    except Exception:
        # La barra fija puede tapar el boton; se fuerza el clic por script.
        driver.execute_script("arguments[0].click();", elemento)
    return elemento


def main():
    solicitante = navegador()
    bibliotecario = navegador()
    try:
        entrar(solicitante, "estudiante1@virginiogomez.cl")
        comprobar("Login del solicitante", "/buscar/" in solicitante.current_url)

        solicitante.get(
            f"{BASE}/buscar/?vista=recursos&fecha={FECHA}&bloque={BLOQUE}&filtrar=1"
        )
        captura(solicitante, "01-busqueda")
        comprobar(
            "La busqueda lista el bloque",
            "Reservar bloque" in solicitante.page_source,
            f"{FECHA} {BLOQUE}",
        )

        clic(solicitante, "//a[contains(., 'Reservar bloque')]")
        captura(solicitante, "02-confirmar")
        comprobar("Pantalla de confirmacion", "Confirmar reserva" in solicitante.page_source)

        clic(solicitante, "//button[contains(., 'Confirmar reserva')]")
        WebDriverWait(solicitante, ESPERA).until(EC.url_contains("/qr/"))
        captura(solicitante, "03-qr")
        codigo = re.search(r"RSV-\d+", solicitante.page_source)
        comprobar("Reserva creada con QR", codigo and "Reserva confirmada" in solicitante.page_source)
        codigo = codigo.group(0)
        print(f"      codigo: {codigo}")

        entrar(bibliotecario, "bibliotecario1@virginiogomez.cl", "/bibliotecario/")
        comprobar("Login del bibliotecario", "/bibliotecario/" in bibliotecario.current_url)

        bibliotecario.get(BASE + "/bibliotecario/?tab=validacion")
        bibliotecario.find_element(By.ID, "id_codigo").send_keys(codigo)
        clic(bibliotecario, "//button[contains(., 'Buscar reserva')]")
        captura(bibliotecario, "04-ticket")
        comprobar("El ticket existe y esta Reservada", "Reservada" in bibliotecario.page_source)

        clic(bibliotecario, "//button[contains(., 'Confirmar entrega')]")
        captura(bibliotecario, "05-en-uso")
        comprobar("La reserva paso a En Uso", "En Uso" in bibliotecario.page_source)

        clic(bibliotecario, "//button[contains(., 'Registrar devolución')]")
        WebDriverWait(bibliotecario, ESPERA).until(
            EC.visibility_of_element_located((By.ID, "modal-devolucion"))
        )
        clic(bibliotecario, "//*[@id='modal-devolucion']//*[@data-modal-confirm]")
        WebDriverWait(bibliotecario, ESPERA).until(
            EC.invisibility_of_element_located((By.ID, "modal-devolucion"))
        )
        captura(bibliotecario, "06-finalizada")
        comprobar("La reserva quedo Finalizada", "Finalizada" in bibliotecario.page_source)
    finally:
        solicitante.quit()
        bibliotecario.quit()

    print()
    print(f"Pasos correctos: {sum(1 for _, ok, _ in pasos if ok)}/{len(pasos)}")
    print(f"Capturas en {SALIDA}")


if __name__ == "__main__":
    main()
