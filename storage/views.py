from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from .models import File, FilePart, FileLog
from .utils import split_and_compress, combine_and_decompress
import uuid

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    if 'file' not in request.FILES:
        return HttpResponseBadRequest("No file provided")
    
    user_id = request.POST.get('user_id', 'anonymous')
    
    uploaded_file = request.FILES['file']
    
    # Проверка размера файла (16MB max)
    if uploaded_file.size > 16 * 1024 * 1024:
        return HttpResponseBadRequest("File size exceeds 16MB limit")
    
    try:
        file_data = uploaded_file.read()
        
        file_obj = File.objects.create(
            original_name=uploaded_file.name,
            size=uploaded_file.size
        )
        
        parts = split_and_compress(file_data, uploaded_file.name)
        
        for part in parts:
            FilePart.objects.create(
                file=file_obj,
                part_number=part['part_number'],
                data=part['data'],
                checksum=part['checksum']
            )
        
        FileLog.objects.create(
            user_id=user_id,
            action='upload',
            file=file_obj,
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'file_id': str(file_obj.id),
            'status': 'File uploaded and split into 16 parts'
        })
    
    except Exception as e:
        return HttpResponseBadRequest(f"Error processing file: {str(e)}")

@require_http_methods(["GET"])
def download_file(request, file_id):
    user_id = request.GET.get('user_id', 'anonymous')

    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        return JsonResponse(
            {'error': 'Invalid file ID format'},
            status=400
        )

    try:
        file_obj = File.objects.get(id=file_uuid)
        parts = FilePart.objects.filter(file=file_obj)
        if parts.count() != 16:
            return HttpResponseBadRequest("Incomplete file parts")
        
        file_data = combine_and_decompress(parts)
        
        FileLog.objects.create(
            user_id=user_id,
            action='download',
            file=file_obj,
            ip_address=get_client_ip(request)
        )
        
        response = HttpResponse(file_data)
        response['Content-Disposition'] = f'attachment; filename="{file_obj.original_name}"'
        return response

    except File.DoesNotExist:
        return JsonResponse(
            {'error': 'File not found'},
            status=404
        )
    except Exception as e:
        return HttpResponseBadRequest(f"Error retrieving file: {str(e)}")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip