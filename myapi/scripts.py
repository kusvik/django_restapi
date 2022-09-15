from typing import Union
from .models import Element, Version
from .loggers import creating_logger
from . import tree
from datetime import timedelta


def create_element(data: dict):
    date = data['updateDate']
    for item in data['items']:
        element = Element.objects.filter(elementId=item['id'])
        if element:
            element = element[0]
            tree.update_trees(element.get_dict(), item, date)
        else:
            tree.update_tree(item, date)
        element = Element(elementId=item['id'],
                          date=date,
                          type=item['type'],
                          url=item['url'],
                          parentId=item['parentId'],
                          size=item['size'])
        creating_logger.debug("Created element " + str(element.get_dict()))
        element.save()
        tree.create_version_from_element(element)


def delete_element(element_id: str) -> bool:
    element = Element.objects.filter(elementId=element_id)
    if element:
        tree.update_size_tree(element[0].parentId, element[0].size)
        tree.delete_tree(element)
        return True
    else:
        return False


def get_element(element_id: str) -> Union[dict, bool]:
    element = Element.objects.filter(elementId=element_id)
    if not element:
        return False
    element = list(element)[0]
    if element.type == 'FILE' or not element.size:
        children = None
    else:
        children = []
        for i in Element.objects.filter(parentId=element.elementId):
            children.append(get_element(i.elementId))
    element = element.get_dict()
    element['children'] = children
    return element


def hours_before(date, hours: int):
    date -= timedelta(hours=hours)
    return date


def get_updates(date) -> list:
    elements = []
    day_before = hours_before(date, 24)
    for element in Element.objects.filter(date__lte=date, date__gte=day_before):
        elements.append(get_element(element.elementId))
    return elements


def get_history(versions_id: str, date_start, date_end) -> list:
    if not Element.objects.filter(elementId=versions_id).exists():
        return []
    versions = []
    if date_start == 0 == date_end:
        for version in Version.objects.filter(elementId=versions_id):
            versions.append(get_element(version.elementId))
    elif date_start == 0:
        for version in Version.objects.filter(elementId=versions_id, date__lt=date_end):
            versions.append(get_element(version.elementId))
    elif date_end == 0:
        for version in Version.objects.filter(elementId=versions_id, date__gte=date_start):
            versions.append(get_element(version.elementId))
    else:
        for version in Version.objects.filter(elementId=versions_id, date__lt=date_end, date__gte=date_start):
            versions.append(get_element(version.elementId))
    return versions
