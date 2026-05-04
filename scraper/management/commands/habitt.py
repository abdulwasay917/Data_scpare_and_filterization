from django.core.management.base import BaseCommand
from products.models import Product, Category, SubCategory
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re


class Command(BaseCommand):

    def get_soup(self, session, url):
        headers = {"User-Agent": "Mozilla/5.0"}
        res = session.get(url, headers=headers, timeout=30)
        return BeautifulSoup(res.text, "html.parser")

    def clean_price(self, text):
        if not text:
            return 0
        nums = re.findall(r"\d+\.?\d*", text.replace(",", ""))
        return float(nums[0]) if nums else 0

    # ✅ CATEGORY + SUBCATEGORY (STRICT FROM MENU)
    def get_menu_data(self, soup, base_url):
        data = []

        categories = soup.select("li.menu-lv-item.menu-lv-1")

        for cat in categories:

            a = cat.find("a")
            if not a:
                continue

            cat_name = a.get_text(strip=True)
            cat_url = a.get("href")

            if not cat_name or not cat_url:
                continue
            if cat_name.lower() in ["sale", "home"]:
                continue
            if "javascript" in cat_url:
                continue

            cat_url = urljoin(base_url, cat_url)

            sub_list = []
            seen = set()


            sub_items = cat.select("li.menu-lv-2 > a, .site-nav-title")

            for sub in sub_items:
                sub_name = sub.get_text(strip=True)
                sub_url = sub.get("href")

                # ❌ strict filters
                if not sub_name or not sub_url:
                    continue
                if "go to" in sub_name.lower():
                    continue
                if sub_name.lower() == cat_name.lower():
                    continue
                if "javascript" in sub_url:
                    continue

                key = sub_name.lower()
                if key in seen:
                    continue
                seen.add(key)

                sub_list.append({
                    "name": sub_name,
                    "url": urljoin(base_url, sub_url)
                })

            data.append({
                "name": cat_name,
                "url": cat_url,
                "subs": sub_list
            })

        return data

    # ✅ PRODUCT SCRAPER
    def scrape_products(self, session, url, category_obj, sub_obj):

        soup = self.get_soup(session, url)
        products = soup.select(".product, .grid-product, .product-item")

        print(f"\n--- SUB: {sub_obj.name}")
        print("URL:", url)
        print("TOTAL ITEMS:", len(products))

        saved = 0

        for p in products:
            try:
                img = p.select_one("img")
                link = p.select_one("a")

                if not img or not link:
                    continue

                name = (img.get("alt") or img.get("title") or "").strip()
                if not name:
                    continue

                image = img.get("src") or img.get("data-src")
                if image and image.startswith("//"):
                    image = "https:" + image

                product_url = urljoin(url, link.get("href"))

                # -------- PRICE -------- #
                price = 0
                json_data = p.get("data-json-product")

                if json_data:
                    try:
                        data = json.loads(json_data)
                        price = data["variants"][0]["price"] / 100
                    except:
                        pass

                if not price:
                    try:
                        detail = self.get_soup(session, product_url)
                        price_tag = detail.select_one(".price, .price__sale")
                        price = self.clean_price(price_tag.get_text()) if price_tag else 0
                    except:
                        price = 0

                # -------- DESCRIPTION -------- #
                description = ""
                try:
                    detail = self.get_soup(session, product_url)
                    desc = detail.select_one(".tab-popup-content")

                    if desc:
                        description = desc.get_text(" ", strip=True)
                except:
                    pass

                # -------- SAVE -------- #
                if not Product.objects.filter(product_name=name).exists():

                    Product.objects.create(
                        product_name=name,
                        description=description,
                        price=price,
                        image=image,
                        category=category_obj,
                        subcategory=sub_obj
                    )

                    saved += 1
                    print("✔ SAVED:", name)

            except Exception as e:
                print("ERROR:", e)
                continue

        return saved

    # ✅ MAIN
    def handle(self, *args, **kwargs):

        base_url = "https://habitt.com/"
        session = requests.Session()

        soup = self.get_soup(session, base_url)

        menu_data = self.get_menu_data(soup, base_url)

        total_saved = 0

        for cat in menu_data:

            print(f"\n===== CATEGORY: {cat['name']} =====")

            cat_obj, _ = Category.objects.get_or_create(name=cat["name"])

            # 🔥 if subcategories exist
            if cat["subs"]:
                for sub in cat["subs"]:

                    sub_obj, _ = SubCategory.objects.get_or_create(
                        name=sub["name"],
                        category=cat_obj
                    )

                    total_saved += self.scrape_products(
                        session,
                        sub["url"],
                        cat_obj,
                        sub_obj
                    )

            else:
                # fallback (rare)
                sub_obj, _ = SubCategory.objects.get_or_create(
                    name=cat["name"],
                    category=cat_obj
                )

                total_saved += self.scrape_products(
                    session,
                    cat["url"],
                    cat_obj,
                    sub_obj
                )

        self.stdout.write(self.style.SUCCESS(
            f"\n🔥 TOTAL PRODUCTS SAVED: {total_saved}"
        ))