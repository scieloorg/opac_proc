## opac_proc

Processamento que coleta os dados desde o Article Meta e armazena eles no MongoDB para serem expostos pelo OPAC.

### Badges:

[![Code Health](https://landscape.io/github/scieloorg/opac_proc/master/landscape.svg?style=flat)](https://landscape.io/github/scieloorg/opac_proc/master)

### Pre-requisitos

- Docker
- Acesso a uma instância de MongoDB com permissão de escita.
- Acesso ao filesystem para escrita de logs

### Pull

Caso você queira baixar a imagem pronta para executar:

```
docker pull scieloorg/opac_proc
```


### docker build

Se você quer contruir a imagem localmente, execute:

```
docker build -t opac_proc .
```


### docker run

Neste exemplo vamos a executar o processamento sobre a coleção com acorônimo: ``spa``, mepeando o volume ``/app/logs`` ao diretorio local: ``/tmp/opac_proc_logs/``.
Também indicamos como acessar a instância do MongoDB para escrever os dados (localhost:27017) e que queremos utilzar o banco: ``opac_test``.
Finalmente indicamos que queremos ativar os logs no nível DEBUG.

```
docker run -v /tmp/opac_proc_logs/:/app/logs/ \
    -e OPAC_PROC_COLLECTION="spa" \
    -e OPAC_PROC_MONGODB_HOST="localhost" \
    -e OPAC_PROC_MONGODB_PORT="27017" \
    -e OPAC_PROC_MONGODB_NAME="opac_test" \
    -e OPAC_PROC_LOG_LEVEL="DEBUG" \
    opac_proc
```

Existem outros parametros de configuração, veja a continuação.


### Configuração com variáveis de ambiente no container:

- ``OPAC_PROC_LOG_LEVEL``: nivel de log (opções: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]). Default: "INFO"
- ``OPAC_PROC_LOG_FILE_PATH``: caminho absoluto do arquivo de log. Default: "<volume-do-container>/app/log/<data-de-hoje>.log"
- ``OPAC_PROC_ARTICLE_META_THRIFT_DOMAIN``: Dominio do article meta para conectar na API Thrift. Default: "articlemeta.scielo.org"
- ``OPAC_PROC_ARTICLE_META_THRIFT_PORT``: Porta do article meta para conectar na API Thrift. Default: "11720"
- ``OPAC_PROC_COLLECTION``: Acrônimo da coleção a ser processada. Default: "spa"
- ``OPAC_PROC_MONGODB_NAME``: Nome do banco mongodb, que armazenara os dados. Default: "opac"
- ``OPAC_PROC_MONGODB_HOST``: Host/IP do banco mongodb. Default: "localhost"
- ``OPAC_PROC_MONGODB_PORT``: Porta do banco mongodb. Default: 27017
- ``OPAC_PROC_MONGODB_USER``: [OPCIONAL] Usuário com acesso ao banco mongodb.
- ``OPAC_PROC_MONGODB_PASS``: [OPCIONAL] Senha do usuário com acesso ao banco mongodb.


### Logs:

O arquivo de log fica armazendo na pasta ``/app/logs/``. O nome do arquivo é a data de execução com formato: ``YYYY-MM-DD.log``.

O diretorio de armazenamento do logs, esta disponível como volume (ver exemplo de docker run acima).


### rodar com docker-compose:

Editar/ajustar os parâmetros no arquivo ``docker-compose.yml`` e executar

```
docker-compose up
```

**OBS**: sempre vai recuparar a imagem de: ``scieloorg/opac_proc``, para rodar com a instância local, troque: ``image: scieloorg/opac_proc`` por: ``build: .``
