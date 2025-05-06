import requests

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


API_BASE_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

# Глобальный словарь для кэширования
cache: dict[str, list[dict]] = {}


def fetch_files_from_api(public_key: str) -> list[dict]:
    """Запрашивает список файлов с API Яндекс.Диска."""
    response = requests.get(API_BASE_URL, params={'public_key': public_key})
    if response.status_code == 200:
        data = response.json()
        return data.get('_embedded', {}).get('items', [])
    else:
        raise ValueError(response.json().get('message', 'Не удалось получить список файлов'))


def filter_files(items: list[dict], file_type: str) -> list[dict]:
    """Фильтрует файлы по указанному типу."""
    if file_type == 'images':
        return [item for item in items if item.get('mime_type', '').startswith('image/')]
    elif file_type == 'documents':
        return [item for item in items if item.get('mime_type', '').startswith('application/') and not (
            item.get('mime_type', '').endswith('zip') or
            item.get('mime_type', '').endswith('x-tar') or
            item.get('mime_type', '').endswith('x-7z-compressed'))]
    elif file_type == 'videos':
        return [item for item in items if item.get('mime_type', '').startswith('video/')]
    elif file_type == 'audio':
        return [item for item in items if item.get('mime_type', '').startswith('audio/')]
    elif file_type == 'archives':
        return [item for item in items if item.get('mime_type', '').startswith('application/') and (
            item.get('mime_type', '').endswith('zip') or
            item.get('mime_type', '').endswith('x-tar') or
            item.get('mime_type', '').endswith('x-7z-compressed'))]
    return items


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница с формой для ввода публичного ключа и отображением списка файлов."""
    public_key = request.GET.get('public_key')
    file_type = request.GET.get('file_type')
    refresh = request.GET.get('refresh')
    items = []
    error = None

    if public_key:
        try:
            # Проверяем кэш или обновляем данные
            if public_key in cache and not refresh:
                items = cache[public_key]
            else:
                items = fetch_files_from_api(public_key)
                cache[public_key] = items

            # Применяем фильтрацию
            items = filter_files(items, file_type)
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Произошла ошибка: {str(e)}"

    return render(request, 'index.html', {
        'items': items,
        'public_key': public_key,
        'error': error,
        'file_type': file_type
    })
