import os
import zipfile


def process_parent_folder():
    # ИСПРАВЛЕНО: добавлено правильное имя системной переменной file
    current_dir = os.path.dirname(os.path.abspath(file))
    # Шаг назад (cd ..) — попадаем в /home/smart/Desktop/igra
    parent_dir = os.path.dirname(current_dir)

    txt_name = "parent_folder_structure.txt"
    zip_name = "parent_archive.zip"

    txt_path = os.path.join(current_dir, txt_name)
    zip_path = os.path.join(current_dir, zip_name)

    # 1. Сбор структуры родительской папки
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Структура родительской папки: {parent_dir}\n")
        f.write("=" * 50 + "\n\n")

        for root, dirs, files in os.walk(parent_dir):
            files = [x for x in files if x not in [txt_name, zip_name]]

            level = root.replace(parent_dir, "").count(os.sep)
            indent = " " * 4 * level
            sub_indent = " " * 4 * (level + 1)

            folder_name = os.path.basename(root)
            if folder_name:
                f.write(f"{indent}[Папка] {folder_name}/\n")

            for file in files:
                f.write(f"{sub_indent}- {file}\n")

    # 2. Создание ZIP-архива родительской папки
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                if file in [txt_name, zip_name]:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, parent_dir)
                zipf.write(full_path, rel_path)

    print("Все готово! Файлы созданы в текущей папке скрипта.")


process_parent_folder()
