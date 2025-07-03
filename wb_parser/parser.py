import requests
from retry import retry


class WbParserBase:
    def __init__(self, headers=None, pages=None):
        self.headers = headers or {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        self.pages = int(pages) if pages else 50

    def get_data_from_json(self, json_file: dict) -> list:
        """Извлекаем из json данные (универсальный вариант, если структура отличается — переопределить в наследнике)"""
        data_list = []
        for data in json_file['data']['products']:
            item = self.parse_product(data)
            if item:
                data_list.append(item)
        return data_list

    def parse_product(self, data: dict) -> dict:
        """Переопределяется в наследниках под нужную структуру"""
        raise NotImplementedError

    def parser(self):
        """Основная функция парсинга, реализуется в наследниках"""
        raise NotImplementedError


class WbParserCatalog(WbParserBase):
    def __init__(self, catalog_url: str, headers=None, pages=None):
        super().__init__(headers, pages)
        self.catalog_url = catalog_url

    def get_catalogs_wb(self) -> dict:
        url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
        headers = {'Accept': '*/*',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        return requests.get(url, headers=headers).json()

    def get_data_category(self, catalogs_wb: dict) -> list:
        catalog_data = []
        if isinstance(catalogs_wb, dict) and 'childs' not in catalogs_wb:
            catalog_data.append({
                'name': f"{catalogs_wb['name']}",
                'shard': catalogs_wb.get('shard', None),
                'url': catalogs_wb['url'],
                'query': catalogs_wb.get('query', None)
            })
        elif isinstance(catalogs_wb, dict):
            catalog_data.append({
                'name': f"{catalogs_wb['name']}",
                'shard': catalogs_wb.get('shard', None),
                'url': catalogs_wb['url'],
                'query': catalogs_wb.get('query', None)
            })
            catalog_data.extend(self.get_data_category(catalogs_wb['childs']))
        else:
            for child in catalogs_wb:
                catalog_data.extend(self.get_data_category(child))
        return catalog_data

    def search_category_in_catalog(self, catalog_url: str, catalog_list: list) -> dict:
        for catalog in catalog_list:
            if catalog['url'] == catalog_url.split('https://www.wildberries.ru')[-1]:
                print(f'найдено совпадение: {catalog["name"]}')
                return catalog
        return None

    def parse_product(self, data: dict) -> dict:
        sku = data.get('id')
        name = data.get('name')
        price = int(data.get("priceU") / 100)
        salePriceU = int(data.get('salePriceU') / 100)
        rating = data.get('rating')
        feedbacks = data.get('feedbacks')
        supplier = data.get('supplier', '')
        print(
            f"SKU:{sku} Цена: {salePriceU} Название: {name} Рейтинг: {rating}, Поставщик: {supplier}")
        return {
            'id': sku,
            'name': name,
            'price': price,
            'salePriceU': salePriceU,
            'rating': rating,
            'feedbacks': feedbacks,
            'supplier': supplier,
        }

    @retry(Exception, tries=-1, delay=0)
    def scrap_page(self, page: int, shard: str, query: str) -> dict:
        print(f'{shard}, {query}')
        url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub' \
            f'&dest=-1257786' \
            f'&locale=ru' \
            f'&page={page}' \
            '&sort=popular&spp=0' \
            f'&{query}'
        r = requests.get(url, headers=self.headers)
        print(f'Статус: {r.status_code} Страница {page} Идет сбор...')
        return r.json()

    def parser(self):
        catalog_data = self.get_data_category(self.get_catalogs_wb())
        try:
            category = self.search_category_in_catalog(
                catalog_url=self.catalog_url, catalog_list=catalog_data)
            data_list = []
            for page in range(1, self.pages + 1):
                data = self.scrap_page(
                    page=page,
                    shard=category['shard'],
                    query=category['query'])
                items = self.get_data_from_json(data)
                print(f'Добавлено позиций: {len(items)}')
                if items:
                    data_list.extend(items)
                else:
                    break
            return data_list
        except TypeError:
            print(
                'Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')


class WbParserSearch(WbParserBase):
    def __init__(self, search_query: str, headers=None, pages=None):
        super().__init__(headers, pages)
        self.search_query = search_query

    @retry(Exception, tries=-1, delay=0)
    def scrap_page(self, query: str, page) -> dict:
        search_query = query.replace(' ', '%20')
        url = f'https://search.wb.ru/exactmatch/ru/common/v13/' \
            'search?ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_dtype=13' \
            '&lang=ru' \
            f'&page={page}' \
            f"&query={search_query}" \
            '&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
        r = requests.get(url, headers=self.headers)
        print(f'Статус: {r.status_code} Страница {page} Идет сбор...')
        return r.json()

    def parse_product(self, data: dict) -> dict:
        try:
            name = data.get('name')
            price = int(data.get("sizes")[0]['price']['basic'] / 100)
            salePriceU = int(data.get('sizes')[0]['price']['product'] / 100)
            rating = data.get('rating')
            feedbacks = data.get('feedbacks')
            supplier = data.get('supplier', '')
            print(
                f"SKU:{data['id']} Цена: {salePriceU} Название: {name} Рейтинг: {rating}, Поставщик: {data.get('supplier', '')}")
            return {
                'id': data.get('id'),
                'name': name,
                'price': price,
                'salePriceU': salePriceU,
                'rating': rating,
                'feedbacks': feedbacks,
                'supplier': supplier,
            }
        except Exception as e:
            print("Ошибка при парсинге товара:", e)
            return None

    def parser(self):
        data_list = []
        try:
            for page in range(1, self.pages + 1):
                data = self.scrap_page(query=self.search_query, page=page)
                items = self.get_data_from_json(data)
                print(f'Добавлено позиций: {len(items)}')
                if items:
                    data_list.extend(items)
                else:
                    break
            return data_list
        except TypeError:
            print(
                'Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')
