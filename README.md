# keyfree - An authentication proxy for Amazon Elasticsearch Service

Keyfree automatically discovers your access keys using Python's boto3. If the
environment you are running keyfree in has already been configured for boto3
then you are good to go!

Recommeded configuration is to run keyfree on an EC2 instance, with an instance
role profile that grants at least the `es:ESHttpGet` permission, in which case
keyfree will automatically discover your role credentials.


## Installing

keyfree is available on pypi:

```
pip install keyfree
```

or on the docker hub:
```
docker pull nickrw/keyfree
```


## Configuring

When you run keyfree it will use boto to discover AWS access credentials and
region configuration. The easiest way to create a configuration file which boto
will discover is by using awscli's "aws configure" command, and entering the
information when prompted.

```
pip install awscli
aws configure
```

Alternatively, you can configure everything through environment variables

```
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=eu-west-1
```


## Running

The keyfree python package includes a bin script which will launch a werkzeug
server for testing purposes. If you run it in production you should use a
production-ready web server such as gunicorn. The docker image does this for
you, but you can do it yourself by pointing a WSGI server at `keyfree.proxy:app`

```
keyfree-proxy-test --endpoint <your endpoint uri>
```

Or using docker

```
# Only the region and endpoint are required if you are running on an EC2
# instance which has role-based access to your ES domain.
docker run -ti --rm \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=your_region \
  -e ENDPOINT=your_endpoint_url \
  -p 9200:9200 \
  nickrw/keyfree
```
