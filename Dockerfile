FROM docker.m.daocloud.io/python:3.10

RUN apt-get update -yq --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
    pkg-config \
    wget \
    cmake \
    curl \
    git \
    vim \
    build-essential \
    libgl1-mesa-glx \
    portaudio19-dev \
    libnss3 \
    libxcomposite1 \
    libxrender1 \
    libxrandr2 \
    libqt5webkit5-dev \
    libxdamage1 \
    libxtst6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "main.py"]
