import os
import glob

def collect_py_files_to_txt(source_dir='bot/database', output_file='database_files.txt'):
    """
    bot/database papkasidagi barcha .py fayllarni nomi bilan ketma-ketlikda
    .txt fayliga jamlaydi
    """
    
    # Papka mavjudligini tekshirish
    if not os.path.exists(source_dir):
        print(f"Xatolik: '{source_dir}' papkasi topilmadi!")
        return
    
    # Barcha .py fayllarni olish (ichki papkalarni ham qo'shish uchun ** rekursiv)
    py_files = glob.glob(os.path.join(source_dir, '**', '*.py'), recursive=True)
    
    # Fayllarni nomi bo'yicha sortlash
    py_files.sort()
    
    if not py_files:
        print(f"'{source_dir}' papkasida .py fayllari topilmadi!")
        return
    
    # Natijalarni yozish
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write("=" * 80 + "\n")
        out_file.write(f"BOT/DATABASE PAPKASIDAGI PYTHON FAYLLARI\n")
        out_file.write(f"Jami fayllar soni: {len(py_files)}\n")
        out_file.write("=" * 80 + "\n\n")
        
        for idx, file_path in enumerate(py_files, 1):
            # Fayl nomini chiroyli ko'rinishda yozish
            relative_path = os.path.relpath(file_path, start=os.path.dirname(source_dir))
            out_file.write(f"\n{'=' * 80}\n")
            out_file.write(f"FAYL #{idx}: {relative_path}\n")
            out_file.write(f"Manzil: {file_path}\n")
            out_file.write(f"{'=' * 80}\n\n")
            
            try:
                # Fayl mazmunini o'qish va yozish
                with open(file_path, 'r', encoding='utf-8') as py_file:
                    content = py_file.read()
                    out_file.write(content)
                    out_file.write("\n\n")
            except Exception as e:
                out_file.write(f"Xatolik: Faylni o'qishda muammo - {str(e)}\n\n")
            
            out_file.write(f"\n{'*' * 80}\n")
            out_file.write(f"FAYL TUGADI: {relative_path}\n")
            out_file.write(f"{'*' * 80}\n\n")
    
    print(f"✅ Yopiq fayl yaratildi: {output_file}")
    print(f"📁 Jami {len(py_files)} ta .py fayli jamlandi")
    print(f"📍 Joylashuv: {os.path.abspath(output_file)}")

def main():
    # Agar xohlasangiz, parametrlarni o'zgartirishingiz mumkin
    source_directory = 'bot/database'  # Manba papka
    output_filename = 'database_files.txt'  # Chiqish fayli nomi
    
    collect_py_files_to_txt(source_directory, output_filename)

if __name__ == "__main__":
    main()