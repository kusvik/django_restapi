from datetime import datetime
from typing import Union

from .loggers import post_logger
from .models import Element


def valid_ids_and_types(data: dict) -> Union[list, bool]:
    ids = []
    for item in data['items']:
        if 'id' in item and 'type' in item and \
                item['type'] in ['FOLDER', 'FILE'] and type(item['id']) is str:
            ids.append(item['id'])
        else:
            return False
    return ids


def valid_keys(item: dict) -> Union[dict, bool]:
    values = {'url': None, 'parentId': None, 'size': None}
    for key in item:
        values[key] = item[key]
    if len(values) > 6:
        return False
    else:
        return values


def valid_time(time: str):
    try:
        time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        return time
    except AttributeError or ValueError:
        return False


def valid_size(item: dict) -> bool:
    if item['type'] == 'FILE':
        return 'size' in item and type(item['size']) is int and item['size'] > 0
    else:
        return 'size' not in item or item['size'] is None


def valid_parent(item: dict, items_ids: list) -> bool:
    if 'parentId' not in item or item['parentId'] is None or item['parentId'] in items_ids:
        return True
    element = Element.objects.filter(elementId=item['parentId'])
    if element:
        return element[0].type == 'FOLDER'
    return False


def valid_url(item: dict) -> bool:
    if item['type'] == 'FOLDER':
        return 'url' not in item or item['url'] is None
    else:
        return 'url' in item and type(item['url']) is str


def changing_type(item: dict) -> bool:
    element = Element.objects.filter(elementId=item['id'])
    if element and element[0].type != item['type']:
        return True
    else:
        return False


def valid_post(data: dict) -> Union[dict, bool]:
    time = valid_time(data['updateDate'])
    if not time:
        post_logger.debug('invalid time')
        return False
    data['updateDate'] = time
    items = data['items']
    items_ids = valid_ids_and_types(data)
    if not items_ids:
        post_logger.debug('some id or type is missing or wrong')
        return False
    for i in range(len(items)):
        items[i] = valid_keys(items[i])
        if len(items[i]) > 5:
            post_logger.debug('excess in ' + str(items[i]))
            return False
        if not (valid_size(items[i]) and valid_parent(items[i], items_ids) and valid_url(items[i])):
            post_logger.debug('size, url or parent is not valid in ' + str(items[i]))
            return False
        if changing_type(items[i]):
            post_logger.debug('type is changing in ' + str(items[i]))
            return False
    return data
