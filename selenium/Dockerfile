FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Pacotes essenciais do sistema + dependências gráficas
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg2 ca-certificates lsb-release \
    python3 python3-pip supervisor \
    xvfb fluxbox x11vnc x11-utils xterm \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libgtk-3-0 \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 libglu1-mesa libxi6 libxrender1 libxext6 libxfixes3 \
    libsodium23 libsodium-dev \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    tesseract-ocr-eng \
    poppler-utils \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    v4l-utils \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    texlive-latex-extra \
    && apt-get clean


# Instala o Google Chrome versão 136
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Instala ChromeDriver 136.0.7103.113
RUN wget https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64


# Instalar e configurar noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify && \
    ln -s /opt/novnc/utils/novnc_proxy /usr/bin/novnc_proxy && \
    chmod +x /opt/novnc/utils/novnc_proxy


# Instalar CoppeliaSim (versão Ubuntu 22.04, ex: 4.3.0)
RUN wget https://downloads.coppeliarobotics.com/V4_10_0_rev0/CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04.tar.xz && \
    tar -xf CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04.tar.xz && \
    rm CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04.tar.xz && \
    mv $(find . -maxdepth 1 -type d -name "CoppeliaSim*" | head -n 1) /opt/CoppeliaSim && \
    chmod +x /opt/CoppeliaSim/coppeliaSim.sh

USER root
RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip && \
    unzip ngrok-stable-linux-amd64.zip && \
    mv ngrok /usr/local/bin/ngrok && \
    chmod 755 /usr/local/bin/ngrok && \
    rm ngrok-stable-linux-amd64.zip




# Instalar pacotes Python (incluindo OCR e PDF)
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Criar usuário não root
RUN useradd -m usuario
USER usuario
WORKDIR /home/usuario

# Copiar supervisord.conf
COPY supervisord.conf /etc/supervisord.conf

# Variável para Tesseract funcionar
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

EXPOSE 5901 8080 8888 19997

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]