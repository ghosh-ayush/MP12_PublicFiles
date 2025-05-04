FROM python:3.6

WORKDIR /usr/src/app

# 1) Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy your code
COPY classify.py data_preload.py models.py server.py train.py utils.py test.py ./

# 3) Prepare folders
RUN mkdir -p data models

# 4) Download the data
RUN python data_preload.py

# 5) Train the free service model (feed-forward on MNIST)
ENV DATASET=mnist
ENV TYPE=ff
RUN python train.py

# 6) Train the premium service model (CNN on KMNIST)
ENV DATASET=kmnist
ENV TYPE=cnn
RUN python train.py

# 7) At runtime, launch your server
CMD ["python", "server.py"]
