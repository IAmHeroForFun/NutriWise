from django.db import models

class Source(models.Model):
    SOURCE_TYPES = [
        ('PDF', 'PDF Ebook'),
        ('EPUB', 'EPUB Ebook'),
        ('WEBSITE', 'Website URL'),
    ]
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('PROCESSING', 'Processing'),
        ('DONE', 'Done'),
        ('FAILED', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    author = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    url = models.URLField(max_length=1000, blank=True)
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPLOADED')
    error_message = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} [{self.get_source_type_display()} - {self.status}]"
