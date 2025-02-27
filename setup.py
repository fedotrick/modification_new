from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    ('', ['lists_data.json']),  # Включаем файл с данными
    ('', ['app.ico'])  # Включаем иконку
]
OPTIONS = {
    'iconfile': 'app.ico',
    'packages': ['toga', 'PIL', 'matplotlib'],
}

setup(
    name="CastingQualityControl",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 