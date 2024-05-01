FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir requests psycopg2
# Waiting for postgres 
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/wait-for-it.sh 
RUN chmod +x /usr/wait-for-it.sh
CMD /usr/wait-for-it.sh postgres:5432 --timeout=5 -- python database_init.py
