# gptTelegramBot
Sample telegram bot with chat gpt integration

## Installation:
Clone repos
```bash 
git clone https://github.com/ai-fn/gptTelegramBot.git
```

Go to workdir `cd gptTelegramBot`

Install via pip: `pip install -r req.txt`

### Configuration
Most configurations are in `setting.py`, others are in backend configurations.

I set many `setting` configuration with my environment variables (such as: `SECRET_KEY`, `DEBUG` and some email configuration parts.) and they did NOT been submitted to the `GitHub`. You can change these in the code with your own configuration or just add them into your environment variables.

### Docker-compose up
Build and run containers as daemon 
`docker-compose up --build -d`

## Run

Modify `bot/setting.py` with database settings, as following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'db_host',
        'PORT': db_port,
    }
}
```

### Create database
Run the following command in PostgreSQL shell:
```sql
craetedb `db_name`;
```

Run the following commands in Terminal:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
```  

### Create super user

Run command in terminal:
```bash
python manage.py createsuperuser
```

### Getting start to run bot
Execute:

```bash
python manage.py bot
```
