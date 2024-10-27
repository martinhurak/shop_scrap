import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Zložka pre ukladanie dát
output_folder = 'data'
os.makedirs(output_folder, exist_ok=True)
# stlpce v csv 
# ked pridaš stlpec musiš pridať aj row 
columns = ['Názov', 'Predajca', 'Cena','Plati do','Poznamka','Kategoria']
# Cesta k CSV súboru
output_path = os.path.join(output_folder, 'shop_data.csv')

# Vytvor prázdny CSV súbor, ak neexistuje
if not os.path.exists(output_path):
    pd.DataFrame(columns=columns).to_csv(output_path, index=False)

# Nastavenie driveru
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.zlacnene.sk/akciovy-tovar")

def scrape_current_page():
    # tu overujem či elementy už na stranke existuju 
    links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.fs-18.fs-m-15.fw-bold.mb-1"))
    )

    unique_links = set(link.get_attribute('href') for link in links)

    for href in unique_links:
        driver.get(href)
        details_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.container.bg-white.px-0.px-md-3"))
        )

        try:
            title = details_section.find_element(By.CSS_SELECTOR, "h1.nadpis-zbozi").text
        except Exception:
            title = "Názov nenájdený"
        try:
            category = details_section.find_element(By.CSS_SELECTOR, "span[itemprop='category']").text
        except Exception:
            category = "Kategoria nenájdená"
        
        # Nájdi všetky kontajnery s informáciami o obchode a cene
        try:
            seller_sections = details_section.find_elements(By.CSS_SELECTOR, "div.col-12[itemprop='offers']")  # Nadradený element obsahujúci meno a cenu

            for seller in seller_sections:
                try:
                    shop_name = seller.find_element(By.CSS_SELECTOR, "span[itemprop='name']").get_attribute("content")
                except Exception:
                    shop_name = "Obchod nenájdený"
                
                try:
                    price = seller.find_element(By.CSS_SELECTOR, "p.fs-20.fw-bold.color-red.mb-0.d-inline-block").text
                except Exception:
                    price = "Cena nenájdená"
                    
                try:
                    priceValidUntil = seller.find_element(By.CSS_SELECTOR, "p[itemprop='priceValidUntil'] strong").text
                except Exception:
                    priceValidUntil = "Platnosť nenájdená"

                try:
                    product_note = seller.find_element(By.CSS_SELECTOR, "p.mb-0.text-muted.fs-10.col-12").text
                except Exception:
                    product_note = ""
                
                # Vytvor prázdny DataFrame so stĺpcami
                new_data = pd.DataFrame(columns=columns)

                # Riadok, ktorý chceš pridať v poradí stĺpcov
                row = [title, shop_name, price, priceValidUntil, product_note, category]

                # Pridanie riadku do DataFrame
                new_data.loc[len(new_data)] = row 
                new_data.to_csv(output_path, mode='a', header=False, index=False)
                print(f"Dáta uložené pre: {title} - {shop_name} - {price}")

        except Exception:
            print("Nepodarilo sa nájsť sekcie predajcov alebo ceny.")

        driver.back()
        # potencialne zbytočne overenie pritomnosti elmentov na stranke  
        '''
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.fs-18.fs-m-15.fw-bold.mb-1"))
        )
        '''
# Loop na prechádzanie stránok s paginátorom
while True:
    scrape_current_page()

    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='Nasledujúca']"))
        )
        next_page_url = next_button.get_attribute('href')

        if next_page_url:
            driver.get(next_page_url)
            # dalšie zbytočne overovanie 
            '''
            WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.fs-18.fs-m-15.fw-bold.mb-1"))
    )
    '''
        else:
            break
    except Exception:
        print("Žiadne ďalšie stránky alebo chyba.")
        break

driver.quit()