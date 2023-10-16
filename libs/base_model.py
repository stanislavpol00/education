from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def added(self):
        return self.created_at

    @property
    def updated(self):
        return self.updated_at

    @property
    def created_by(self):
        if hasattr(self, "added_by"):
            return self.added_by
        return None
