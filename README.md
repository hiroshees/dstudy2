# ログインの仕組み（Django版）

## 
django-allauthを使わないでDjangoのユーザの仕組みののでメールアドレスでのログインに変更した仕組み


## 変更手順
```
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```

```
python manage.py makemigrations
python manage.py migrate

```
