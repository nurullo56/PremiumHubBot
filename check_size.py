import os

def get_project_size(path='.'):
    total_size = 0
    # Loyihadagi barcha papka va fayllarni aylanib chiqish
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Agar fayl ramziy havola (link) bo'lmasa, hajmini qo'shish
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def format_size(size):
    # Hajmni o'qishga qulay formatga o'tkazish
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

# Loyihaning asosiy papkasida turib ishga tushiring
project_path = "."  # Hozirgi turgan papka
size_in_bytes = get_project_size(project_path)

print(f"--- Loyiha ma'lumotlari ---")
print(f"Papka: {os.path.abspath(project_path)}")
print(f"Umumiy hajmi: {format_size(size_in_bytes)}")