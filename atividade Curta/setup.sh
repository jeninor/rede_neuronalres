#!/bin/bash

# Criar ambiente virtual (se ainda não existir)
python -m venv meu_ambiente

# Ativar ambiente virtual
source meu_ambiente/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Exibir pacotes instalados para debug
pip list
