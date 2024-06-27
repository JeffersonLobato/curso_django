## Deploy de aplicação Django

- Para este tutorial, vamos levar em consideração que o usuário linux se chama ubuntu e tem um diretório /home/ubuntu, caso seu usuário tenha outro nome com outro diretório, você terá que substituir pelo nome correto sempre que /home/ubuntu aparecer.

- Vou considerar também que ao criar o projeto você utilizou o ponto ao final como no exemplo abaixo, isso mexe com a organização dos diretórios do projeto.
```Shell
django-admin startproject MeuProjeto .
```

- Se for o caso, você pode criar um arquivo .env com todas variáveis da aplicação, neste caso não será necessário, mas em um ambiente profissional em que há uma equipe trabalhando com github, por exemplo, seria interessante, tanto por motivo de segurança, já que você poderia dar um gitignore no .env e evitar enviar informações sigilosas da aplicação, como por motivo de não precisar passar as credenciais reais da aplicação que está em produção pra toda equipe de desenvolvimento, entre outros motivos.

- Carregando variáveis, caso utilize o .env:
```Python
from dotenv import load_dotenv # precisa instalar com o PIP
import os
load_dotenv()

os.environ.get('DJANGO_KEY')
```

- Exemplo de arquivo .env
```
DJANGO_KEY = 'Gerar uma chave nova para colocar aqui'
STATUS_DEBUG = False
NAME_DB = 'nomeDoBancoDeDados'
USER_DB = 'nomeDoUsuario'
PASS_DB = 'SENHA_DO_USER_DB'
HOST_DB = 'localhost'
PASSWORD_EMAIL = 'senha_de_email_de_envio'
```

## Preparando o ambiente

Ainda no seu ambiente de desenvolvimento, DENTRO DO SEU AMBIENTE VIRTUAL, faça o seguinte comando no terminal.

```Shell
pip freeze > requirements.txt
```

Esse comando vai criar um arquivo requirements.txt contendo todos os pacotes instalados no seu projeto com a exata versão, isso vai ser muito útil mais pra frente.

Copie todas as pastas da sua aplicação menos a pasta do seu ambiente virtual e todos os arquivos, com exceção do .env, se houver, e do arquivo de extensão .db, caso você esteja utilizando um Sqlite3, por exemplo, já que este arquivo é o banco de dados do projeto em desenvolvimento, no projeto em produção é interessante iniciar um novo banco.

Observe que neste caso nós estamos enviando também as migrations, você pode reparar que dentro de cada diretório de cada App tem uma pasta migrations, o ideal é não enviar as migrations, principalmente quando o banco em produção é um, por exemplo, MySql e o bando do ambiente de desenvolvimento é outro, mas para fins didáticos vamos manter as migrations do projeto como estão, vamos entender que você vai utilizar o mesmo tipo de banco de dados nos dois ambientes.

Para o ambiente de produção o seu settings.py precisa estar configurado com o com DEBUG = False, assim como você pode fazer algumas outras modificações, por exemplo, digamos que você está utilizando um Sqlite3 em desenvolvimento e um MySql em produção, pra isso você não enviou as migrations do ambiente de desenvolvimento e fará um makemigrations no ambiente de produção para que suas models sirvam para criar tabelas no MySql, logo você faria algo parecido com isso.

```Python

# Nosso exemplo leva em consideração de que as variáveis estão armazenadas no .env

DEBUG = os.getenv('STATUS_DEBUG', 'False').lower() in ['true', '1', 't']

if DEBUG = True:
	DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': BASE_DIR / 'db.sqlite3',

	    }
	
	}
else:

	DATABASES = {
	
	        'default': {
	
	            'ENGINE': 'django.db.backends.mysql',
	
	            'NAME': os.environ.get('NAME_DB'),
	
	            'USER': os.environ.get('USER_DB'),
	
	            'PASSWORD': os.environ.get('PASS_DB'),
	
	            'HOST': os.environ.get('HOST_DB'), # ou endereço do seu servidor MySQL
	
	            'PORT': '3306', # porta padrão do MySQL
	
	        }
	
	    }
```

Voltando ao nosso projeto, ainda dentro de settings.py configure o domínio que será usado para acessar a aplicação, somente domínios autorizados vão conseguir acessar sua aplicação e configure o DEBUG para False.

```python
ALLOWED_HOSTS = ['meudominio.com', '192.168.0.10', '127.0.0.1']
DEBUG = False # Ou faça como no exemplo anterior, utilizando variáveis de ambiente armazenadas no .env
```

Agora no servidor linux, já com os arquivos do projeto no local, vamos fazer o seguinte, dentro do diretório /home/ubuntu/ coloque o diretório do seu projeto, exemplo, se o diretório for MeuProjeto, o caminho do seu projeto será /home/ubuntu/MeuProjeto e aqui ficarão todos os arquivos e diretórios do seu projeto.

Dentro do diretório raiz do projeto execute os seguintes comandos.

- Atualize o repositório e pacotes do linux.
```Shell
sudo apt update
sudo apt upgrade
```

- Criar um ambiente virtual python (talvez seja necessário instalar o venv do python).
```shell
sudo apt install python3-venv
python3 -m venv NomeDoSeuAmbienteVirtual
```

- Entrar no ambiente virtual (troque env pelo nome do seu ambiente virtual e confira se realmente o arquivo activate encontra-se neste diretório)
```shell
source ./env/bin/activate
```

- Atualize o pip
```Shell
pip install --upgrade pip
```

- Instalar os pacotes do arquivo requirements.txt
```shell

pip install -r requirements.txt
# talvez precise antes de tudo instalar o pip com sudo apt-get install pip
```

- Caso esteja utilizando o MySql no ambeinte de produção, instalar o mysqlclient com o pip dentro do ambiente virtual
```Shell
pip install mysqlclient
```

- Fazer o makemigrations e migrate
```python
python manage.py makemigrations
python manage.py migrate
```

- Criar uma chave aleatória para colocar no .env, se estiver utilizando variáveis de ambiente, ou substituir diretamente a SECRET_KEY do Django no arquivo settings.py
```Shell
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> get_random_secret_key()
#Copiar a chave e colocar no arquivo .env na variável DJANGO_KEY

>>> exit()
```

- Caso você tenha configurado o MEDIA_ROOT e o STATIC_ROOT, deverá inserir o seguinte trecho de código no arquivo urls.py do diretório raiz.
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	...
    ]
if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- Caso esteja utilizando arquivos estáticos, como CSS ou Javascript, faça um collectstatic

```Shell
python manage.py collectstatic
```

## Instalação e configuração do uWSGI e NGINX

O uWSGI é um servidor de aplicação que suporta várias linguagens, neste caso vamos utilizado como uma interface entre a aplicação Django e o Nginx que fará o papel de servidor Web, este vai tratar as requisições Web.

- Agora vamos instalar o uWSGI e outros pacotes que vão melhorar o processo de instalação de pacotes Python:

```Shell
sudo apt install python3-dev
sudo apt install build-essential libssl-dev libffi-dev python-dev-is-python3
pip install wheel
pip install uwsgi
```

- Agora vamos instalar o Nginx

```Shell
sudo apt install nginx
sudo /etc/init.d/nginx start # iniciar o serviço
```

Vamos criar com o nano (editor de texto do linux pelo terminal) um arquivo uwsgi_params dentro do diretório do projeto, mesmo diretório que tem o arquivo manage.py

- Criar um arquivo com o nome uwsgi_params
```
nano uwsgi_params
```

- Conteúdo do arquivo
```Shell

uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;
```

Agora vamos criar um arquivo de configuração do NGINX.

- Vamos abrir um arquivo no caminho /etc/nginx/sites-available/ com o nome meu_projeto_nginx.conf
```Shell
nano /etc/nginx/sites-available/meu_projeto_nginx.conf
# Substitua meu_projeto_nginx pelo nome do seu projeto
```

- Conteúdo do arquivo, preste atenção nos comentários dentro do conteúdo, não copie e cole sem modificar para ficar de acordo com o seu projeto, retira o # das linhas que precisar usar.
```Shell
upstream django {
    server unix:///home/ubuntu/MeuProjeto/mysite.sock; 
    # Comentário: substitua MeuProjeto pelo nome do diretório do seu projeto, o arquivo mysite.sock será criado automaticamente. Lembrando que /home/ubuntu é porque neste exemplo estamos utilizando um usuário com o nome o ubuntu e esse diretório é o diretório do usuário, onde estamos instalando nossa aplicação.
}

server {
    listen      80;
    # Em caso de configurações pra conexões https pela porta 443, sugiro que aprofundar-se na documentação do nginx.
    server_name DOMINIO;
    # Comentário: substitua DOMINIO pelo endereço IP ou pelo domínio por onde seu projeto será acessado.
    charset     utf-8;

    client_max_body_size 75M; 
    # Comentário: aqui você configura o tamanho máximo de MB em uma requisição, neste caso cada requisição pode conter no máximo 75M, faça adapte ao seu projeto.

	# Comentário: aqui substitua MeuProjeto pelo nome do diretório do seu projeto
	# Comentário: este trecho só será necessário se o diretório media existir e se você tiver configurado o MEDIA_ROOT do seu projeto
    #location /media  {
    #    alias /home/ubuntu/MeuProjeto/media; 
	#}

	# Comentário: aqui substitua MeuProjeto pelo nome do diretório do seu projeto
	# Comentário: este trecho só será necessário se o diretório staticfiles existir e se você tiver configurado o STATIC_ROOT do seu projeto
    #location /static {
    #   alias /home/ubuntu/MeuProjeto/staticfiles;
    #}

    #location / {
    #    uwsgi_pass  django; # django é o nome do upstream configurado no início do arquivo
    #    include     /home/ubuntu/Prontuario/uwsgi_params; 
        # Comentário: aqui substitua MeuProjeto pelo nome do diretório do seu projeto
    #}

	# Comentário: se por ventura você for utilizar websockets no seu projeto, arqui vai um exemplo de configuração
    #location /ws/ {
        # Comentário: encaminha solicitações WebSocket para o Daphne
    #    proxy_pass http://127.0.0.1:8001;
    #    proxy_http_version 1.1;
	#	proxy_set_header Upgrade $http_upgrade;
    #    proxy_set_header Connection "Upgrade";
    #    proxy_set_header Host $host;

    #}
}

```

- Remova o arquivo default do nginx
```Shell
sudo rm -rf /etc/nginx/sites-enabled/default
```

- Criar um symlink em sites-enabled (Lembre de substituir o meu_projeto_nginx pelo nome que você colocou quando criou o arquivo)
```Shell
ln -s ~/etc/nginx/sites-available/meu_projeto_nginx.conf /etc/nginx/sites-enabled/
```

-  Resetar o Nginx
``` Shell
sudo /etc/init.d/nginx restart
```

- Criar um arquivo ini do uWSGI dentro do diretório do projeto, onde tem o arquivo manage.py, lembre de substituir pelo nome do seu projeto
```Shell
nano /home/ubuntu/MeuProjeto/meu_projeto_uwsgi.ini
```

- Conteúdo do arquivo, faça as modificações necessárias, conforme o que está nos comentários.
```Shell
[uwsgi]
chdir           = /home/ubuntu/MeuProjeto # substitua pelo nome do diretório do seu projeto
module          = NomeDoProjeto.wsgi # Aqui é o nome do projeto, aquele foi dado quando foi feito o django-admin startproject NomeDoProjeto .
home            = /home/ubuntu/MeuProjeto/env # substitua pelo nome do diretório do seu projeto e env pelo nome da venv que você criou
master          = true
processes       = 10
socket          = /home/ubuntu/MeuProjeto/mysite.sock # substitua pelo nome do diretório do seu projeto
vacuum          = true
chmod-socket    = 666

```

-  Configurando o uWSGI em modo Emperor, lembrando de alterar para o nome do seu projeto onde estiver meu_projeto ou MeuProjeto

```Shell
sudo mkdir /etc/uwsgi
sudo mkdir /etc/uwsgi/vassals
sudo ln -s /home/ubuntu/MeuProjeto/meu_projeto_uwsgi.ini /etc/uwsgi/vassals/

```

- Criar o arquivo .service para automatizar o início e restart do serviço uwsgi, lembrando de alterar para o nome do seu projeto onde estiver meu_projeto ou MeuProjeto
```Shell
nano /etc/systemd/system/meu_projeto_uwsgi.service
```

- Conteúdo do arquivo, lembrando de alterar para o nome do seu projeto onde estiver meu_projeto ou MeuProjeto e env pelo nome da venv que você criou, lembrando que /home/ubuntu é considerando que você está utilizando um usuário com o nome ubuntu, então lá em User também tem que ser o nome do seu usuário correto.
```Shell
[Unit]
Description=Django VPS uWSGI Emperor
After=syslog.target

[Service]
ExecStart=/home/ubuntu/MeuProjeto/env/bin/uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data
RuntimeDirectory=uwsgi
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all
User=ubuntu

[Install]
WantedBy=multi-user.target

```

Agora vamos dar as permissões necessárias e ativas os serviços. Não esqueça de usar o nome correto do arquivo.
```Shell

sudo chmod 664 /etc/systemd/system/meu_projeto_uwsgi.service

sudo systemctl daemon-reload

sudo systemctl enable meu_projeto_uwsgi.service

sudo systemctl start meu_projeto_uwsgi.service

# Caso queira verificar o status
sudo systemctl status meu_projeto_uwsgi.service

# Caso queira verificar verificar o log
journalctl -u meu_projeto_uwsgi.service

```

- Reinicie o Nginx

```Shell
sudo systemctl restart nginx
```

Pronto, neste momento sua aplicação tem que está rodando no IP ou domínio que você configurou no arquivo de configuração do nginx e no settings.py do django. Lembre que DEBUG = True no settings.py somente em ambiente de desenvolvimento, python manage.py runserver só para ambiente de desenvolvimento. Para um deploy profissional, sempre deixe DEBUG = False, e utilize como servidor o uWSGI com Nginx, ou Apache, ou Gunicorn entre outros que são específicos para esse tipo de funcionalidade, são mais robustos e escaláveis.
