from django.contrib import admin
from django.urls import path
from storage.views import upload_file, download_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/files/', upload_file, name='upload-file'),
    path('api/files/<uuid:file_id>/', download_file, name='download-file'),
]