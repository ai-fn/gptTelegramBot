FROM python:3.11.5-slim

RUN mkdir code

WORKDIR /code

ADD . /code/

RUN pip install -r requirements.txt

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py createcachetable \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_sepuruser('root', 'root@gmail.com', 'root')" \
    && python manage.py bot
