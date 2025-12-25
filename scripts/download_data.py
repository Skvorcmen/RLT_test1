"""
Скрипт для скачивания JSON файла с Google Drive
"""
import gdown
import os
import sys

# ID файла из Google Drive URL
FILE_ID = "1BZOYxhDmMGJrSbPdcQgQjh0HRzN1YZt5"
OUTPUT_FILE = "data/videos_data.json"

def download_file():
    """Скачивает файл с Google Drive"""
    os.makedirs("data", exist_ok=True)
    
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    print(f"Скачивание файла с Google Drive...")
    print(f"URL: {url}")
    
    try:
        gdown.download(url, OUTPUT_FILE, quiet=False, fuzzy=True)
        
        if os.path.exists(OUTPUT_FILE):
            file_size = os.path.getsize(OUTPUT_FILE)
            print(f"Файл успешно скачан: {OUTPUT_FILE} ({file_size} bytes)")
            return True
        else:
            print("Ошибка: файл не был скачан")
            return False
    except Exception as e:
        print(f"Ошибка при скачивании: {e}")
        return False

if __name__ == "__main__":
    success = download_file()
    sys.exit(0 if success else 1)

