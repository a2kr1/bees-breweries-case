FROM openjdk:11-slim

# Variáveis de ambiente
ENV SPARK_VERSION=3.4.1
ENV HADOOP_VERSION=3
# ENV DELTA_VERSION=2.4.0


# Instalação de dependências básicas
RUN apt-get update && apt-get install -y \
    curl wget python3 python3-pip python3-dev openjdk-11-jdk ca-certificates bash gnupg && \
    rm -rf /var/lib/apt/lists/*

# Instalação do Apache Spark a partir do arquivo histórico da Apache
RUN wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

RUN apt-get update && apt-get install -y procps

# Configurações do Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Instala pacotes Python do projeto
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r /tmp/requirements.txt

# Configuração Delta Lake
# ENV PYSPARK_SUBMIT_ARGS="--packages io.delta:delta-core_2.12:${DELTA_VERSION} pyspark-shell"

# Copia configurações do Spark
COPY spark-defaults.conf $SPARK_HOME/conf/spark-defaults.conf

# Diretório de trabalho
WORKDIR /home/project
COPY . /home/project
RUN chmod -R 777 /home/project

# Comando padrão ao entrar no container
CMD [ "bash", "tail", "-f", "/dev/null" ]
