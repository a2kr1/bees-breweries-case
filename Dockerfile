FROM jupyter/pyspark-notebook:spark-3.4.1

# Instalações básicas
RUN apt-get update && \
    apt-get install -y curl wget gnupg software-properties-common python3 python3-pip bash procps && \
    pip3 install --upgrade pip

# Variáveis de ambiente
ENV SPARK_VERSION=3.4.1
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Instala o Spark com suporte a Hadoop
# RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
#     | tar -xz -C /opt/ && \
#     mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

# Copia o .tgz para dentro da imagem
COPY auxiliar/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz /tmp/spark.tgz

# Extrai localmente sem baixar
RUN tar -xzf /tmp/spark.tgz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

# Copia requirements e instala dependências
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Instala as dependências do projeto
RUN pip install --no-cache-dir pyspark==3.4.1 delta-spark==2.4.0

# Expõe as portas da UI do Spark e Jupyter Notebook (caso sejam utilizadas)
EXPOSE 4040
EXPOSE 8888

# Define variável de ambiente padrão para localização do código Python
ENV PYTHONPATH=/home/project

# Copia o projeto para dentro do container
COPY . /home/project

# Diretório de trabalho
WORKDIR /home/project

# Cria a pasta de warehouse do Hive
RUN mkdir -p /opt/spark-warehouse
