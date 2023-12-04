FROM python:3.6
WORKDIR /app

RUN mkdir ~/.streamlit
RUN pip install --upgrade pip
COPY config.toml ~/.streamlit/config.toml
COPY credentials.toml ~/.streamlit/credentials.toml
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
WORKDIR /app
COPY . .
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
