# Artifact-migration

Artifact-migration - программа для переноса Docker образов и Helm чартов из публичных репозиториев во внутренний.

> На данный момент поддерживается перенос артефактов в Nexus репозитории.

## Зависимости

Для корректной работы программы ей необходимы следующие зависимости:

* Библиотеки Python:
  
  * pyyaml
  
  * argparse

* Helm

* Docker

* curl

## Запуск программы

Artifact-migration принимает на вход следующие аргументы:

```plain text
file             путь к yaml файлу со списком артефактов
-h,   --help     справка
-m,   --mode     режим работы программы. save - сохраняет артефакты локально, `migrate` - мигрирует артефакты из публичного репозитория во внутренний
-u               логин для внутреннего репозитория
-p               пароль для внутреннего репозитория
-dr              адрес Docker репозитория
-hr              адрес Helm репозитория
-l               устанавливает уровень логирования
```

### Список артефактов

Для передачи списка артефактов используется файл расширения yaml со следующим содержимым:

```yaml
dockerImages:
  - name: nginx
    tags:
      - 1.22
      - 1.23-perl

helmCharts:
  - name: minio
    repo: charts.min.io
    tags:
      - 4.0.15
      - 4.0.13
```

В файле могут быть описаны одновременно Docker образы и Helm чарты.

Docker образы описываются в блоке `dockerImages`. Каждый артефакт должен иметь имя `name` и список из тегов `tags`. Список `tags` должен содержать минимум один тег.

Helm чарты описываются в блоке `helmCharts`. Каждый артефакт должен иметь имя `name`, публичный репозиторий `repo` и версию чарта `tags`. Список `tags` должен содержать минимум один тег.

### Миграция артефактов

Для миграции артефактов во внетренний репозиторий выполните следующуу команду:

```shell
python main.py [FILE] --mode migration -u [LOGIN] -p [PASSWORD] -dr [DOCKER_REGISTRY_URL] -hr [HELM_REGISTRY_URL]
```

Первым аргументом передается путь к yaml файлу со списком артефактов, далее передаются: логин для внутреннего репозитория, пароль для внутреннего репозитория, адрес Docker репозитория и/или адрес Helm репозитория.

### Сохранение артефактов локально

Для сохранения артефактов выполните следующуу команду:

```shell
python main.py [FILE] --mode save
```

### Выполнение программы в Gitlab CI

Для запуска программы в пайплайне Gitlab CI соберите образ с настройкой среды выполнения. Для этого в репозитории есть Dockerfile, в котором описана установка необходимых зависимостей.

Джоба для запуска миграции выглядит следующим образом:

```yaml
stages:
    - migration

docker-migrate:
    stage: migration
    image: apervakov/artifact-migration:0.1.1-alfa
    services:
        - docker:20.10.16-dind
    variables:
        DOCKER_HOST: tcp://docker:2375
        DOCKER_TLS_CERTDIR: ""
    script:
        - python3 /main.py ./artifacts.yaml -m migration -u [LOGIN] -p [PASSWORD] -dr [DOCKER_REGISTRY_URL]
```
