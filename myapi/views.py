import json

from rest_framework.response import Response
from rest_framework.views import APIView

from . import scripts
from .validators import *
from .loggers import *

not_valid = {'code': 400, 'message': 'Validation Failed'}
not_found = {'code': 404, 'message': 'Item not found'}


class PostElement(APIView):
    @staticmethod
    def post(request):
        data = json.loads(request.body)
        post_logger.debug("Posting" + str(data))
        if not valid_post(data):
            post_logger.debug("Validation Failed")
            return Response(data=not_valid, status=400)
        scripts.create_element(data)
        post_logger.debug("Posted successfully")
        return Response()


class DeleteElement(APIView):
    @staticmethod
    def delete(request, element_id):
        delete_logger.debug(f"Deleting {element_id} and its children")
        if scripts.delete_element(element_id):
            delete_logger.debug("Deleted successfully")
            return Response()
        else:
            delete_logger.debug("Nothing found")
            return Response(data=not_found, status=404)


class GetElement(APIView):
    @staticmethod
    def get(request, element_id):
        get_logger.debug(f"Getting {element_id} and its children")
        element = scripts.get_element(element_id)
        if element:
            get_logger.debug("Got it")
            return Response(data=element)
        else:
            get_logger.debug("Nothing found")
            return Response(data=not_found, status=404)


class GetUpdates(APIView):
    @staticmethod
    def get(request):
        date = valid_time(request.query_params['date'])
        if not date:
            return Response(data=not_valid, status=400)
        updates = scripts.get_updates(date)
        if updates:
            return Response(data=updates)
        else:
            return Response(data=not_found, status=404)


class GetVersions(APIView):
    @staticmethod
    def get(request, versions_id):
        date_start, date_end = 0, 0
        params = request.query_params
        if 'dateStart' in params:
            date_start = params['dateStart']
        if 'dateEnd' in params:
            date_end = params['dateEnd']
        versions = scripts.get_history(versions_id, date_start, date_end)
        if versions:
            return Response(data=versions)
        else:
            return Response(data=not_found, status=404)
