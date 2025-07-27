# Base otimizada com Spark 3.3.2 e Hadoop 3 pré-instalados
FROM bitnami/spark:3.3.2

# Usuário root para permissões de instalação
USER root

# Instala dependências adicionais (se necessário)
RUN install_packages python3 python3-pip curl bash procps

# Instala bibliotecas Python do projeto
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# Cria diretórios de trabalho
WORKDIR /home/project

# Copia os diretórios do projeto
COPY ./src /home/project/src
COPY ./scripts /home/project/scripts
COPY ./data /home/project/data
COPY ./notebooks /home/project/notebooks
COPY ./tests /home/project/tests

# Copia arquivos de configuração (opcional)
COPY spark-defaults.conf /opt/bitnami/spark/conf/

# Define o diretório padrão dentro do container
WORKDIR /home/project/scripts

CMD ["python3", "main.py"]
