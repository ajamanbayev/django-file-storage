import zipfile
import hashlib
from io import BytesIO

def split_and_compress(file_data, original_name):
    """Split file into 16 parts and compress each"""
    file_size = len(file_data)
    part_size = file_size // 16
    parts = []
    
    for i in range(16):
        start = i * part_size
        end = (i + 1) * part_size if i < 15 else file_size
        part_data = file_data[start:end]
        
        # Create ZIP for the part
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(f'part_{i}', part_data)
        
        zip_data = zip_buffer.getvalue()
        parts.append({
            'part_number': i,
            'data': zip_data,
            'checksum': hashlib.sha256(zip_data).hexdigest()
        })
    
    return parts

def combine_and_decompress(parts):
    """Combine parts back into original file"""
    combined_data = BytesIO()
    
    # Sort parts by part number to ensure correct order
    sorted_parts = sorted(parts, key=lambda x: x.part_number)
    
    for part in sorted_parts:
        with zipfile.ZipFile(BytesIO(part.data)) as zipf:
            for name in zipf.namelist():
                combined_data.write(zipf.read(name))
    
    return combined_data.getvalue()