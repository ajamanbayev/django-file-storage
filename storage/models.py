from django.db import models
import uuid

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.original_name} ({self.size} bytes)"

class FilePart(models.Model):
    file = models.ForeignKey(File, related_name='parts', on_delete=models.CASCADE)
    part_number = models.PositiveSmallIntegerField()
    data = models.BinaryField()
    checksum = models.CharField(max_length=64)

    class Meta:
        unique_together = ('file', 'part_number')

    def __str__(self):
        return f"Part {self.part_number} of {self.file.original_name}"

class FileLog(models.Model):
    ACTION_CHOICES = [
        ('upload', 'Upload'),
        ('download', 'Download'),
    ]

    user_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_id} {self.action} {self.file} at {self.timestamp}"