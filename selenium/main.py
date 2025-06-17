import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
import os
import time
import tempfile
from urllib.parse import urlparse


# URL da apresentação
url = "https://docs.google.com/presentation/d/e/2PACX-1vRsKsGIYXF09ku4d9xdNvovuimXBuQOYixWvF8lXKu8l8wNQns0QjA98q599zNH2X1lnhc4VR76GLLz/pub?start=false&loop=false&delayms=3000"

# Chrome headless
# Chrome headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Solução para "user data directory is already in use"
temp_profile = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={temp_profile}")

driver = webdriver.Chrome(service=Service(), options=options)

# Primeiro: abrir o domínio onde os cookies são válidos
driver.get("https://docs.google.com")  # Isso precisa acontecer ANTES de setar os cookies

# Primeiro, agrupar cookies por domínio
from collections import defaultdict

cookies_by_domain = defaultdict(list)
with open("cookies.json") as f:
    cookies = json.load(f)
    for cookie in cookies:
        for key in ["sameSite", "storeId", "hostOnly", "id"]:
            cookie.pop(key, None)
        cookies_by_domain[cookie["domain"].lstrip(".")].append(cookie)

# Para cada domínio único, navega até o domínio e injeta os cookies dele
for domain, domain_cookies in cookies_by_domain.items():
    url = f"https://{domain}"
    try:
        driver.get(url)
        time.sleep(2)
        for cookie in domain_cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"❌ Erro ao adicionar cookie {cookie.get('name')} para domínio {domain}: {e}")
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")

# Agora acessar o link da apresentação
time.sleep(5)

driver.get(url)
time.sleep(5)

# Cria pasta para slides
os.makedirs("slides", exist_ok=True)

# Quantidade de slides estimada (ajuste conforme necessário)
num_slides = 10

for i in range(num_slides):
    driver.save_screenshot(f"slides/slide_{i+1}.png")
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys("\ue014")  # seta →
    time.sleep(1)

driver.quit()

# Converte PNGs em PDF
images = []
for i in range(1, num_slides + 1):
    path = f"slides/slide_{i}.png"
    if os.path.exists(path):
        img = Image.open(path).convert("RGB")
        images.append(img)

if images:
    images[0].save("slides/apresentacao_final.pdf", save_all=True, append_images=images[1:])
    print("✅ PDF gerado em: slides/apresentacao_final.pdf")
else:
    print("⚠️ Nenhum slide capturado.")
