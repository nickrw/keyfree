FROM python:3
EXPOSE 9200
CMD gunicorn --bind '0.0.0.0:9200' keyfree.proxy:app

RUN pip install --use-wheel --upgrade pip wheel setuptools gunicorn

# Install dependencies first, so this layer is cached
COPY requirements.txt /usr/local/src/requirements.txt
RUN pip install --use-wheel -r /usr/local/src/requirements.txt

COPY MANIFEST.in README* requirements* setup.py /usr/local/src/keyfree/
COPY keyfree/ /usr/local/src/keyfree/keyfree/
RUN cd /usr/local/src/keyfree; python setup.py bdist_wheel
RUN pip install /usr/local/src/keyfree/dist/*.whl
