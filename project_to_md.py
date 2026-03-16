import os
import sys
from pathlib import Path

# --- НАСТРОЙКИ ---

# Имя выходного файла
OUTPUT_FILENAME = "project_structure.md"

# Папки, которые нужно игнорировать
IGNORE_DIRS = {
    'venv', 'env', '.venv', 'virtualenv',
    'node_modules',
    '.git', '.svn', '.hg',
    '__pycache__',
    '.idea', '.vscode', '.eclipse',
    'dist', 'build', 'egg-info',
    '.pytest_cache', '.mypy_cache',
    'coverage', 'htmlcov'
}

# Расширения файлов, которые нужно игнорировать (бинарники, картинки и т.д.)
IGNORE_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd',
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.exe', '.dll', '.so', '.dylib',
    '.pdf', '.doc', '.docx',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.db', '.sqlite', '.sqlite3',
    '.class', '.o', '.a'
}

# -----------------

def get_language_hint(file_path):
    """Возвращает подсказку для подсветки синтаксиса в MD на основе расширения."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.sh': 'bash',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.sql': 'sql',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.txt': 'text'
    }
    ext = Path(file_path).suffix.lower()
    return ext_map.get(ext, '')

def is_text_file(file_path):
    """Простая проверка, является ли файл текстовым (чтобы не ломаться на бинарниках)."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return False
        return True
    except Exception:
        return False

def generate_tree(root_path, ignore_dirs, script_abs_path):
    """Генерирует строковое представление дерева проекта."""
    lines = []
    root = Path(root_path)
    
    # Сортировка для стабильного вывода
    def get_key(p):
        return (not p.is_dir(), p.name.lower())

    for current_root, dirs, files in os.walk(root):
        # Сортировка директорий на месте, чтобы os.walk шел в нужном порядке
        dirs.sort(key=lambda x: x.lower())
        
        # Фильтрация директорий (исключаем ненужные и сам скрипт если он в папке)
        dirs[:] = [
            d for d in dirs 
            if d not in ignore_dirs 
            and Path(current_root) / d != script_abs_path.parent
        ]

        # Вычисляем относительный путь для красивого вывода
        rel_path = Path(current_root).relative_to(root)
        depth = len(rel_path.parts)
        
        # Если это корень
        if depth == 0:
            lines.append(f"{root.name}/")
        else:
            # lines.append(f"{'  ' * depth}{rel_path}/") # Можно включить, если нужно дублирование папок
            pass

        # Добавляем файлы в текущей папке
        files.sort(key=lambda x: x.lower())
        for file in files:
            file_path = Path(current_root) / file
            
            # Пропускаем сам скрипт
            if file_path.resolve() == script_abs_path:
                continue
            
            # Пропускаем игнорируемые расширения
            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            indent = "  " * (depth + 1)
            lines.append(f"{indent}{file}")

    return "\n".join(lines)

def generate_content(root_path, ignore_dirs, script_abs_path):
    """Генерирует содержимое файлов с подсветкой синтаксиса."""
    content_blocks = []
    root = Path(root_path)

    for current_root, dirs, files in os.walk(root):
        # Та же фильтрация директорий
        dirs[:] = [
            d for d in dirs 
            if d not in ignore_dirs 
            and Path(current_root) / d != script_abs_path.parent
        ]

        files.sort(key=lambda x: x.lower())
        for file in files:
            file_path = Path(current_root) / file

            # Пропускаем сам скрипт
            if file_path.resolve() == script_abs_path:
                continue

            # Пропускаем игнорируемые расширения
            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue
            
            # Пропускаем бинарные файлы
            if not is_text_file(file_path):
                continue

            try:
                # Читаем файл
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                rel_path = file_path.relative_to(root)
                lang = get_language_hint(file_path)
                
                block = f"## `{rel_path}`\n\n"
                block += f"```{lang}\n{code}\n```\n\n"
                content_blocks.append(block)
                
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

    return "\n".join(content_blocks)

def main():
    # Определяем путь к текущему скрипту (абсолютный)
    script_path = Path(__file__).resolve()
    # Путь к проекту (откуда запущен скрипт)
    project_path = Path.cwd()

    print(f"Scanning project: {project_path}")
    print(f"Excluding script: {script_path}")

    # 1. Генерируем дерево
    print("Generating structure tree...")
    tree = generate_tree(project_path, IGNORE_DIRS, script_path)

    # 2. Генерируем содержимое
    print("Reading file contents...")
    content = generate_content(project_path, IGNORE_DIRS, script_path)

    # 3. Формируем итоговый Markdown
    markdown_output = f"# Project Dump\n\n"
    markdown_output += f"Generated by `{script_path.name}`\n\n"
    markdown_output += f"## 📂 Structure\n\n```text\n{tree}\n```\n\n"
    markdown_output += f"## 📄 File Contents\n\n{content}"

    # 4. Записываем в файл
    output_file = project_path / OUTPUT_FILENAME
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        print(f"Success! Saved to {output_file}")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()