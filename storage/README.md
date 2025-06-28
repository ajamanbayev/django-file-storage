# File Storage Service

A Django-based service for storing files by splitting them into 16 compressed parts.

## Features

- Upload files (max 16MB)
- Download files by ID
- Files are split into 16 equal parts and compressed
- Activity logging for all operations

## API Endpoints

### Upload File

`POST /api/files/`

Parameters:
- `file`: The file to upload
- `user_id`: User identifier

Response:
```json
{
    "file_id": "UUID",
    "status": "File uploaded and split into 16 parts"
}