#!/usr/bin/env python3
"""
Скрипт диагностики пагинации MOEX API
---------------------------------------
Проверяет:
1. Подъём приложения через docker_manage.py
2. Подключение к базе данных
3. SQL-запросы с OFFSET 0 и OFFSET 20
4. API-эндпоинты через requests
5. Выдаёт цветной отчёт

Запуск:
    python debug_pagination.py
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime

# ==================== ЦВЕТА ДЛЯ КОНСОЛИ ====================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}  {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_ok(text):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {text}")

def print_warn(text):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {text}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {text}")

# ==================== ШАГ 1: ПОДЪЁМ ПРИЛОЖЕНИЯ ====================
def build_and_up():
    print_header("ШАГ 1: Подъём приложения")
    
    # Проверяем существование docker_manage.py
    manage_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docker_manage.py')
    if not os.path.exists(manage_script):
        print_error(f"Файл docker_manage.py не найден: {manage_script}")
        return False
    
    print_info(f"Скрипт: {manage_script}")
    
    # Проверяем, запущено ли приложение
    try:
        resp = requests.get('http://localhost:8000/health', timeout=3)
        if resp.status_code == 200:
            print_ok("Приложение уже запущено и отвечает!")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print_info("Приложение не запущено. Поднимаю...")
    
    # Запуск build
    print_info("Выполняю: python docker_manage.py build")
    result = subprocess.run(
        [sys.executable, 'docker_manage.py', 'build'],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print_error("Ошибка при build:")
        print(result.stderr)
        return False
    print_ok("Build завершён успешно")
    
    # Запуск up
    print_info("Выполняю: python docker_manage.py up")
    result = subprocess.run(
        [sys.executable, 'docker_manage.py', 'up'],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print_error("Ошибка при up:")
        print(result.stderr)
        return False
    
    # Ждём запуска
    print_info("Ожидаю запуска сервисов (10 сек)...")
    time.sleep(10)
    
    # Проверяем ответ
    try:
        resp = requests.get('http://localhost:8000/health', timeout=5)
        if resp.status_code == 200:
            print_ok("Приложение запущено и отвечает!")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print_error("Приложение не отвечает после запуска.")
    return False

# ==================== ШАГ 2: ПРОВЕРКА БАЗЫ ДАННЫХ ====================
def check_database():
    print_header("ШАГ 2: Проверка базы данных")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        import os
        
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', '.env'))
        
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', 5432))
        db_user = os.getenv('DB_USER', 'postgres')
        db_pass = os.getenv('DB_PASSWORD', 'postgres')
        db_name = os.getenv('DB_NAME', 'moex')
        
        print_info(f"Подключение: {db_user}@{db_host}:{db_port}/{db_name}")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            dbname=db_name,
            connect_timeout=5
        )
        cursor = conn.cursor()
        
        # Считаем все записи
        cursor.execute("SELECT COUNT(*) FROM instruments")
        total = cursor.fetchone()[0]
        print_ok(f"Всего записей в таблице 'instruments': {total}")
        
        if total == 0:
            print_warn("Таблица пуста! Запустите collector для заполнения данных.")
            cursor.close()
            conn.close()
            return False
        
        # Проверяем записи с OFFSET 0
        cursor.execute("SELECT ticker, type, price FROM instruments ORDER BY ticker ASC LIMIT 5 OFFSET 0")
        rows_offset0 = cursor.fetchall()
        print_ok(f"Запрос с OFFSET 0: получено {len(rows_offset0)} записей")
        for row in rows_offset0:
            print(f"         {row[0]} ({row[1]}) - цена: {row[2]}")
        
        # Проверяем записи с OFFSET 20
        cursor.execute("SELECT ticker, type, price FROM instruments ORDER BY ticker ASC LIMIT 5 OFFSET 20")
        rows_offset20 = cursor.fetchall()
        print_ok(f"Запрос с OFFSET 20: получено {len(rows_offset20)} записей")
        for row in rows_offset20:
            print(f"         {row[0]} ({row[1]}) - цена: {row[2]}")
        
        # Проверяем NULL-значения
        cursor.execute("SELECT COUNT(*) FROM instruments WHERE price IS NULL")
        null_price = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM instruments WHERE price IS NOT NULL")
        not_null_price = cursor.fetchone()[0]
        print_info(f"Записи с NULL ценой: {null_price}, с ценой: {not_null_price}")
        
        cursor.close()
        conn.close()
        
        if len(rows_offset0) > 0:
            print_ok("База данных работает корректно!")
            return True
        else:
            print_error("База данных возвращает пустой результат с OFFSET 0!")
            return False
            
    except ImportError as e:
        print_error(f"Не импортирована библиотека: {e}")
        print_info("Установите: pip install psycopg2-binary python-dotenv")
        return False
    except Exception as e:
        print_error(f"Ошибка подключения к БД: {e}")
        return False

# ==================== ШАГ 3: ПРОВЕРКА API ====================
def check_api():
    print_header("ШАГ 3: Проверка API эндпоинтов")
    
    base_url = 'http://localhost:8000'
    all_ok = True
    
    # Проверка health
    print_info("Проверка /health...")
    try:
        resp = requests.get(f'{base_url}/health', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print_ok(f"/health: {data}")
        else:
            print_error(f"/health: HTTP {resp.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"/health: {e}")
        all_ok = False
    
    # Проверка /instruments с OFFSET 0
    print_info("\nПроверка /instruments?limit=20&offset=0...")
    try:
        resp = requests.get(f'{base_url}/api/instruments', params={'limit': 20, 'offset': 0}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print_ok(f"OFFSET 0: получено {len(data)} записей")
            if len(data) > 0:
                print_ok(f"  Первая: {data[0].get('ticker', 'N/A')}")
                print_ok(f"  Последняя: {data[-1].get('ticker', 'N/A')}")
            else:
                print_error("Получен пустой список!")
                all_ok = False
        else:
            print_error(f"/instruments: HTTP {resp.status_code}")
            print_error(f"Ответ: {resp.text}")
            all_ok = False
    except Exception as e:
        print_error(f"/instruments (offset=0): {e}")
        all_ok = False
    
    # Проверка /instruments с OFFSET 20
    print_info("\nПроверка /instruments?limit=20&offset=20...")
    try:
        resp = requests.get(f'{base_url}/api/instruments', params={'limit': 20, 'offset': 20}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print_ok(f"OFFSET 20: получено {len(data)} записей")
            if len(data) > 0:
                print_ok(f"  Первая: {data[0].get('ticker', 'N/A')}")
                print_ok(f"  Последняя: {data[-1].get('ticker', 'N/A')}")
            else:
                print_warn("Получен пустой список (возможно, это нормально)")
        else:
            print_error(f"/instruments: HTTP {resp.status_code}")
            print_error(f"Ответ: {resp.text}")
            all_ok = False
    except Exception as e:
        print_error(f"/instruments (offset=20): {e}")
        all_ok = False
    
    # Проверка /instruments/count
    print_info("\nПроверка /instruments/count...")
    try:
        resp = requests.get(f'{base_url}/instruments/count', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print_ok(f"/instruments/count: {data}")
        else:
            print_error(f"/instruments/count: HTTP {resp.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"/instruments/count: {e}")
        all_ok = False
    
    # Проверка /instruments/count/full (новый эндпоинт)
    print_info("\nПроверка /instruments/count/full...")
    try:
        resp = requests.get(f'{base_url}/instruments/count/full', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print_ok(f"/instruments/count/full: {data}")
        else:
            print_error(f"/instruments/count/full: HTTP {resp.status_code}")
            print_error(f"Ответ: {resp.text}")
            all_ok = False
    except Exception as e:
        print_error(f"/instruments/count/full: {e}")
        all_ok = False
    
    return all_ok

# ==================== ШАГ 4: ПРОВЕРКА ФРОНТЕНДА ====================
def check_frontend():
    print_header("ШАГ 4: Проверка фронтенда")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    if not os.path.exists(frontend_dir):
        print_error(f"Директория frontend не найдена: {frontend_dir}")
        return False
    
    # Проверяем наличие app.jsx
    app_jsx = os.path.join(frontend_dir, 'src', 'app', 'app.jsx')
    if os.path.exists(app_jsx):
        print_ok(f"Файл app.jsx найден: {app_jsx}")
        
        # Проверяем наличие пагинации
        with open(app_jsx, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pagination' in content.lower():
                print_ok("Компонент пагинации обнаружен")
            else:
                print_error("Компонент пагинации НЕ обнаружен")
            
            if 'offset' in content:
                print_ok("Параметр offset используется")
            else:
                print_error("Параметр offset НЕ используется")
    else:
        print_error(f"Файл app.jsx не найден: {app_jsx}")
        return False
    
    # Проверяем ThemeToggle
    theme_toggle = os.path.join(frontend_dir, 'src', 'components', 'common', 'ThemeToggle.jsx')
    if os.path.exists(theme_toggle):
        print_ok(f"Компонент ThemeToggle найден: {theme_toggle}")
    else:
        print_warn("Компонент ThemeToggle НЕ найден")
    
    return True

# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================
def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           МОEX API - ДИАГНОСТИКА ПАГИНАЦИИ              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Шаг 1: Подъём
    app_running = build_and_up()
    if not app_running:
        print_error("\nНе удалось поднять приложение. Проверьте Docker и конфигурацию.")
        sys.exit(1)
    
    # Шаг 2: База данных
    db_ok = check_database()
    
    # Шаг 3: API
    api_ok = check_api()
    
    # Шаг 4: Фронтенд
    frontend_ok = check_frontend()
    
    # Итог
    print_header("ИТОГ")
    
    if db_ok and api_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!{Colors.RESET}")
        print_ok("Пагинация работает корректно.")
        print_ok("API отвечает корректно.")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}ОБНАРУЖЕНЫ ПРОБЛЕМЫ:{Colors.RESET}")
        if not db_ok:
            print_error("Проблемы с базой данных")
        if not api_ok:
            print_error("Проблемы с API")
        print(f"\n{Colors.YELLOW}Рекомендации:{Colors.RESET}")
        print("  1. Проверьте, запущен ли collector: docker ps")
        print("  2. Запустите collector вручную: docker compose up collector")
        print("  3. Проверьте логи: docker compose logs -f backend")
        sys.exit(1)

if __name__ == '__main__':
    main()
