__Foodgram - это  сайт, на котором пользователи могут публиковать свои рецепты, 
добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Зарегистрированным пользователям доступен сервис «Список покупок», позволяющий 
создавать список продуктов, которые нужно купить для приготовления выбранных блюд.__
Доступен по адресу: http://188.120.254.254:8000/

__Используемые технологии__:
    - БД - `PostgreSQL`
    - фреймворк - `Django`
    - авторизация в приложении - `djoser token authentication`
    - контейнеризация приложения - `Docker (+DockerHub)`


__ИНСТРУКЦИЯ ПО ЗАПУСКУ__:

1. Скопируйте проект себе на github `fork`, скачайте проект из репозитория на компьютер `git clone`.

__ЛОКАЛЬНЫЙ ЗАПУСК НА КОМПЬЮТЕРЕ:__

2. В корневой директории проекта создайте файл `touch .env` с переменными окружения.
Список переменных доступен в файле .envexample.

4. Создайте и активируйте виртуальную среду, установите зависимости:
   - `cd foodgram_backend`
   - `python3 -m venv env`
   - `source env/bin/activate`
   - `python3 -m pip install --upgrade pip`
   - `pip install -r requirements.txt`

5. Запустите Dockercompose из корневой папки проекта с помощью команд:
- `sudo docker compose -f docker-compose.yml pull`
- `sudo docker compose -f docker-compose.yml down`
- `sudo docker compose -f docker-compose.yml up -d`

6. Сделайте миграции и соберите статику с помощью команд:
- `sudo docker compose -f docker-compose.yml exec backend python manage.py migrate`
- `sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic`
- `sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/ `


__ЗАПУСК НА ВИРТУАЛЬНОМ СЕРВЕРЕ:__

2. В корневой директории сервера создайте новую директорию `mkdir foodgram`.
   
3. В директории foodgram создайте файл `touch .env` с переменными окружения.
Список переменных доступен в файле .envexample

4. Поменяйте настройки nginx
`sudo nano /etc/nginx/sites-enabled/default`

- Добавьте строки:

`server {`  
`server_name АДРЕС ВАШЕГО ВНЕШНЕГО ХОСТА (ИЗ ALLOWED_HOSTS);`  
`   location / {  `  
`	 proxy_set_header Host $http_host;`  
`	 proxy_pass http://127.0.0.1:8000;`  
`    }`  
`}`

- Получите сертификат SSL
  `sudo certbot --nginx`

- Перезапустите nginx
  `sudo systemctl reload nginx`

5. В настройках репозитория на гитхаб добавьте переменные в Secrets:

- DOCKER_PASSWORD: <пароль от Docker Hub>
- DOCKER_USERNAME: <имя пользователя Docker Hub>
- HOST: <ip сервера>
- USER: <имя пользователя сервера>
- PASSWORD: <пароль для доступа к серверу>


Теперь после каждого выполнения команды `git push` обновления будут грузиться на сервер.
Если что-то пойдет не так, почистите сервер от лишних образов, контейнеров и файлов.
- `docker system prune -a`
- `docker volume prune`
- `du -sh * | sort -h` (выведет список самых крупных файлов/директорий.)


Разработчик бэкенда проекта:
- Дарья Новогородская
