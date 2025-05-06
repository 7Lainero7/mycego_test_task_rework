import requests

from django.shortcuts import render


API_BASE_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"


def index(request):
    """Главная страница с формой для ввода публичного ключа и отображением списка файлов."""

    public_key = request.GET.get('public_key')
    file_type = request.GET.get('file_type')  # Получаем выбранный тип файла
    items = []
    error = None

    if public_key:
        # Запрос к API Яндекс.Диска
        response = requests.get(API_BASE_URL, params={'public_key': public_key})
        if response.status_code == 200:
            data = response.json()
            items = data.get('_embedded', {}).get('items', [])
            # Фильтрация по типу файла

            if file_type == 'images':
                items = [item for item in items if item.get('mime_type', '').startswith('image/')]
            elif file_type == 'documents':
                items = [item for item in items if item.get('mime_type', '').startswith('application/')]
            elif file_type == 'videos':
                items = [item for item in items if item.get('mime_type', '').startswith('video/')]
            elif file_type == 'audio':
                items = [item for item in items if item.get('mime_type', '').startswith('audio/')]
            elif file_type == 'archives':
                items = [item for item in items if item.get('mime_type', '').startswith('application/') and (
                    item.get('mime_type', '').endswith('zip') or item.get('mime_type', '').endswith('x-tar'))]
        else:
            error = response.json().get('message', 'Не удалось получить список файлов')

    return render(request, 'index.html', {'items': items, 'public_key': public_key, 'error': error, 'file_type': file_type})
