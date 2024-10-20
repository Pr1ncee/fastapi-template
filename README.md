# FastAPI Custom Template

## Overview

This repository servers as a template for applications build with FastAPI web framework

I included the whole basic functionality based on my experience most projects used:
1. Pipenv with pre-listed libraries;
2. Makefile for improving developer experience;
3. Docker & Docker Compose;
4. Dockerized PostgreSQL;
5. Ready-to-use Alembic;
6. Ready-to-use SQLAlchemy with CRUDMixin;
7. Authentication middleware;
8. RequestService for making external HTTP requests
9. Ready-to-use test environment.

The application uses **Python 3.12** and all newest versions as in 2024-10-20. 

## Prerequisites

- Pipenv
- Docker & Docker Compose
- Make

## How to run

Create `.env` file in the project root directory and fill it up according to `.env.sample` file.

To spin up the whole application, you can enter:

```shell
make start
```

To shut it down, you can enter:

```shell
make down
```

## Explore other available Make commands

To display all available commands and their description, you can enter:

```shell
make help
```