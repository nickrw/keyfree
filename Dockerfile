FROM python:3
EXPOSE 9200
RUN pip install --use-wheel --upgrade pip wheel setuptools
COPY . /usr/local/src/keyfree
RUN cd /usr/local/src/keyfree; python setup.py bdist_wheel
RUN pip install /usr/local/src/keyfree/dist/*.whl gunicorn
CMD gunicorn --bind '0.0.0.0:9200' keyfree.proxy:app
