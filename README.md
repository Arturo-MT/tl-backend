## Installing

1. Clone the repo: `git clone repo_url`
2. Navigate to the folder: `cd tl_backend`
3. Build Docker Image (Musta have Docker Desktop Installed): `docker-compose build`
4. Start services: `docker-compose up`
   
Additionally you can run the project with the following command: `docker-compose up --build --no-recreate -d`
   
5. It will be running at: `http://localhos:8000/`
6. Create superuser: `docker-compose run web python manage.py createsuperuser`
7. Access to admin at: `http://localhos:8000/admin/` with the credentials you just created


## Making migrations

1. `docker-compose run web python manage.py makemigrations`
2.  `docker-compose run web python manage.py migrate`
