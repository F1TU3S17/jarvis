import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



class WebPageParser:
    def __init__(self, delay=1, timeout=10, api_key=None, cx=None):
        self.session = requests.Session()
        self.delay = delay
        self.timeout = timeout
        self.api_key = api_key
        self.cx = cx
        
        # Настройка retry стратегии
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Более реалистичные headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_content(self, soup):
        """Извлекает основной контент страницы"""
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '.article-body'
        ]
        
        # Пробуем найти основной контент
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return content
        
        # Если не нашли, берём body
        return soup.find('body') or soup

    def clean_text(self, soup):
        """Очищает текст от ненужных элементов"""
        # Удаляем скрипты, стили, навигацию
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                           'aside', 'advertisement', '.ad', '.ads']):
            element.decompose()
        
        # Извлекаем текст из параграфов, заголовков и списков
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div'])
        
        texts = []
        for element in text_elements:
            text = element.get_text(strip=True)
            if len(text) > 20:  # Игнорируем слишком короткие тексты
                texts.append(text)
        
        return ' '.join(texts)

    def extract_metadata(self, soup):
        """Извлекает метаданные страницы"""
        metadata = {}
        
        # Заголовок
        title = soup.find('title')
        metadata['title'] = title.get_text(strip=True) if title else 'Без заголовка'
        
        # Описание
        description = soup.find('meta', attrs={'name': 'description'})
        metadata['description'] = description.get('content', '') if description else ''
        
        # Ключевые слова
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        metadata['keywords'] = keywords.get('content', '') if keywords else ''
        
        # Open Graph данные
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['og_title'] = og_title.get('content', '')
            
        og_description = soup.find('meta', property='og:description')
        if og_description:
            metadata['og_description'] = og_description.get('content', '')
        
        return metadata

    def parse_page(self, url, extract_links=False):
        """Парсит одну страницу"""
        try:
            self.logger.info(f"Парсинг: {url}")
            
            # Проверяем валидность URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Невалидный URL")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Определяем кодировку
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем основной контент
            main_content = self.extract_content(soup)
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'metadata': self.extract_metadata(soup),
                'content': self.clean_text(main_content),
                'content_length': len(self.clean_text(main_content)),
                'links': []
            }
            
            # Извлекаем ссылки если нужно
            if extract_links:
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    link_text = link.get_text(strip=True)
                    if link_text:
                        result['links'].append({
                            'url': absolute_url,
                            'text': link_text
                        })
            
            return result
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout для {url}")
            return {'url': url, 'error': 'Timeout'}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка запроса для {url}: {e}")
            return {'url': url, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка для {url}: {e}")
            return {'url': url, 'error': str(e)}

    def parse_multiple_pages(self, urls, extract_links=False):
        """Парсит несколько страниц с задержкой"""
        results = []
        
        for i, url in enumerate(urls):
            result = self.parse_page(url, extract_links)
            results.append(result)
            
            # Добавляем задержку между запросами
            if i < len(urls) - 1:
                time.sleep(self.delay)
        
        return results

    def web_search(self, query, num_results=5):
        """
        Выполняет поиск и возвращает контент с первых num_results сайтов
        
        Args:
            query (str): Поисковый запрос
            num_results (int): Количество сайтов для парсинга (по умолчанию 5)
            
        Returns:
            list: Список строк с контентом найденных сайтов
        """
        if not self.api_key or not self.cx:
            raise ValueError("API ключ и CX должны быть установлены для поиска")
        
        try:
            # Выполняем поиск через Google Custom Search API
            search_url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.api_key,
                'cx': self.cx,
                'num': num_results
            }
            
            self.logger.info(f"Выполняем поиск: {query}")
            search_response = requests.get(search_url, params=params, timeout=self.timeout)
            search_response.raise_for_status()
            
            search_results = search_response.json()
            
            # Получаем ссылки из результатов поиска
            urls = []
            items = search_results.get("items", [])
            for item in items[:num_results]:
                urls.append(item["link"])
            
            if not urls:
                self.logger.warning("Не найдено ссылок в результатах поиска")
                return []
            
            # Парсим найденные страницы
            parsed_results = self.parse_multiple_pages(urls, extract_links=False)
            
            # Формируем список строк с контентом
            content_list = []
            for result in parsed_results:
                if 'error' not in result and result.get('content'):
                    # Формируем строку с информацией о сайте
                    title = result['metadata'].get('title', 'Без заголовка')
                    url = result['url']
                    content = result['content']
                    
                    formatted_content = f"Заголовок: {title}\nURL: {url}\nКонтент: {content}\n{'-'*80}"
                    content_list.append(formatted_content)
                else:
                    # Добавляем информацию об ошибке
                    error_msg = f"Ошибка при парсинге {result['url']}: {result.get('error', 'Неизвестная ошибка')}"
                    content_list.append(error_msg)
            
            return content_list
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка поиска: {e}")
            return [f"Ошибка поиска: {e}"]
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка поиска: {e}")
            return [f"Неожиданная ошибка поиска: {e}"]
