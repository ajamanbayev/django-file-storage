from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import File, FilePart, FileLog
import os

class FileStorageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_file = SimpleUploadedFile(
            "test.txt",
            b"This is a test file content that needs to be more than 16 bytes to split properly.",
            content_type="text/plain"
        )

    def test_file_upload(self):
        response = self.client.post('/api/files/', {
            'file': self.test_file,
            'user_id': 'test_user'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('file_id' in response.json())
        
        file_id = response.json()['file_id']
        self.assertTrue(File.objects.filter(id=file_id).exists())
        
        file_obj = File.objects.get(id=file_id)
        self.assertEqual(file_obj.parts.count(), 16)
        
        self.assertTrue(FileLog.objects.filter(file=file_obj, action='upload').exists())

    def test_file_download(self):
        # Загрузка файла
        upload_response = self.client.post('/api/files/', {
            'file': self.test_file,
            'user_id': 'test_user'
        })
        file_id = upload_response.json()['file_id']
        
        # Скачивание файла
        download_response = self.client.get(f'/api/files/{file_id}/?user_id=test_user')
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(
            download_response['Content-Disposition'],
            f'attachment; filename="test.txt"'
        )
        
        # Проверка лога
        file_obj = File.objects.get(id=file_id)
        self.assertTrue(FileLog.objects.filter(file=file_obj, action='download').exists())

    def test_file_size_limit(self):
        large_file = SimpleUploadedFile(
            "large.txt",
            os.urandom(17 * 1024 * 1024),  # 17MB
            content_type="text/plain"
        )
        response = self.client.post('/api/files/', {
            'file': large_file,
            'user_id': 'test_user'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds 16MB limit", str(response.content))

    def test_invalid_file_id(self):
        response = self.client.get('/api/files/invalid-id/?user_id=test_user')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file ID", str(response.content))