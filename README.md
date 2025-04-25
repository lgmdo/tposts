# 🐦 tposts

Uma plataforma de microblogging feita com Django + DRF.

# Como rodar o projeto

Para rodar este projeto, é necessário:

1. Ter o **Docker** instalado em sua máquina.
2. Criar um arquivo `.env` com base nas configurações fornecidas no `.env-example`.

Com isso pronto, basta executar o seguinte comando para iniciar o servidor localmente:

```sh
docker compose up
```

O servidor será iniciado em `localhost`, utilizando a porta definida na variável `SERVER_PORT` do seu arquivo `.env`.

## Exemplos

Se `SERVER_PORT=8000`, os principais endpoints serão:

- API: `http://localhost:8000`
- Documentação da API: `http://localhost:8000/docs`
- Admin do Django: `http://localhost:8000/admin`

## Criar um usuário administrador

Para criar um superusuário (admin), execute o comando abaixo:

```sh
docker compose exec tposts poetry run python src/manage.py createsuperuser
```

# Uso do Makefile

O uso do Makefile é opcional, mas ele facilita a execução de alguns comandos comuns no projeto. Abaixo estão os comandos disponíveis:

### Aplicar as migrations do Django
```sh
make migrate
```

### Rodar os testes automatizados (Django)
```sh
make test
```

### Rodar o linter (usando Ruff)
```sh
make lint
```

### Rodar a checagem de tipos (usando Pyright)
```sh
make type-check
```

