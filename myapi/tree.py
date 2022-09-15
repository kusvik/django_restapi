from typing import Union
from django.db import IntegrityError
from .models import Element, Version
from .loggers import delete_logger, creating_logger


def create_version_from_element(element: Element):
    try:
        Version.objects.create(elementId=element.elementId,
                               date=element.date,
                               type=element.type,
                               url=element.url,
                               parentId=element.parentId,
                               size=element.size)
    except IntegrityError:
        version = Version.objects.get(elementId=element.elementId, date=element.date)
        version.size = element.size
        version.save()


def delete_tree(requested: Union[list, iter]):
    if requested:
        requested_children = []
        for element in requested:
            element_children = Element.objects.filter(parentId=element.elementId)
            delete_logger.debug(element.elementId + " deleted")
            element.delete()
            for element_child in element_children:
                requested_children.append(element_child)
        return delete_tree(requested_children)


def update_time_tree(parent_id: str, date):
    if parent_id is not None:
        parent = Element.objects.get(elementId=parent_id)
        parent.date = date
        creating_logger.debug("Updated element " + str(parent.get_dict()))
        parent.save()
        create_version_from_element(parent)
        update_time_tree(parent.parentId, date)


def update_time_and_size_tree(parent_id: str, date, size: int):
    if parent_id is not None:
        parent = Element.objects.get(elementId=parent_id)
        parent.date = date
        if parent.size is None:
            parent.size = size
        else:
            parent.size += size
        creating_logger.debug("Updated element " + str(parent.get_dict()))
        parent.save()
        create_version_from_element(parent)
        update_time_and_size_tree(parent.parentId, date, size)


def update_size_tree(parent_id: str, size: int):
    if parent_id is not None:
        parent = Element.objects.get(elementId=parent_id)
        parent.size -= size
        creating_logger.debug("Updated element " + str(parent.get_dict()))
        parent.save()
        update_size_tree(parent.parentId, size)


def update_tree(item: dict, date):
    if not item['size']:
        update_time_tree(item['parentId'], date)
    else:
        update_time_and_size_tree(item['parentId'], date, item['size'])


def update_trees(old_values: dict, new_values: dict, date):
    size_not_changed = old_values['type'] == 'FOLDER' or old_values['size'] == new_values['size']
    parent_changed = new_values['parentId'] != old_values['parentId']

    if size_not_changed:
        update_time_tree(new_values['parentId'], date)
        if parent_changed:
            update_time_tree(old_values['parentId'], date)
    else:
        if parent_changed:
            update_time_and_size_tree(old_values['parentId'], date, -old_values['size'])
            update_time_and_size_tree(new_values['parentId'], date, +new_values['size'])
        else:
            difference = new_values['size'] - old_values['size']
            update_time_and_size_tree(new_values['parentId'], date, difference)
