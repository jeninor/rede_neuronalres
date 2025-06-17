# Usar a imagem oficial do Python
FROM python:3.12

# Atualiza pacotes e instala dependências do OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    v4l-utils \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# COPY requirements.txt .
# COPY practice-1-ImageRetrieval-inf692.ipynb .
# COPY jpg-20250402T134911Z-001.zip .
# COPY datasplits.mat .
COPY . .

RUN unzip jpg-20250402T134911Z-001.zip -d /src

# Cria e ativa o ambiente virtual
RUN python -m venv venv \
    && . venv/bin/activate \
    && pip install --upgrade pip \
    && pip3 install -r requirements.txt

ENV PATH="/venv/bin:$PATH"

# Expone el puerto de Jupyter Notebook
EXPOSE 8888

ENTRYPOINT ["/bin/bash", "-c"]

CMD ["/src/venv/bin/jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token='' --NotebookApp.password=''"]

