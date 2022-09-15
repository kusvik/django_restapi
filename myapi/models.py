from django.db import models


class Element(models.Model):
    elementId = models.CharField(max_length=255, primary_key=True)
    date = models.DateTimeField()
    url = models.CharField(max_length=255, null=True)
    parentId = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=6)
    size = models.IntegerField(null=True)

    def get_dict(self) -> dict:
        return {'id': self.elementId, 'date': self.date, 'type': self.type,
                'parentId': self.parentId, 'size': self.size, 'url': self.url}


class Version(models.Model):
    elementId = models.CharField(max_length=255)
    date = models.DateTimeField()
    url = models.CharField(max_length=255, null=True)
    parentId = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=6)
    size = models.IntegerField(null=True)

    class Meta:
        unique_together = [['elementId', 'date']]
