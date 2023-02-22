# obugs-backend

# Developer Setup
## Unix

```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python 
```

## Windows

```
python -m venv .wenv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
"$(get-location)" > .\.wenv\Lib\site-packages\d2notes.pth
python main.py
```

python manage.py makemigrations backend
python manage.py sqlmigrate backend 0001
