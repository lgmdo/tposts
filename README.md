# 🐦 tposts

Uma plataforma de microblogging feita com Django + DRF.

# Rodar o projeto

PAra rodar o projeto é necessário ter o Docker instalado e um .env com a configuração indicada no .env-example.
Após isso basta executar os comandos seguintes para iniciar o server localmente:

```sh
docker compose up
docker compose exec tposts poetry run python src/manage.py migrate
docker compose exec tposts poetry run python src/manage.py runserver
```

para criar um usuário admin rode o comando:

```sh
docker compose exec tposts poetry run python src/manage.py createsuperuser
```



