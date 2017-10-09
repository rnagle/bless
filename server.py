import os
import json
import random
import sys

from flask import Flask, request

from bless.aws_lambda.bless_lambda import lambda_handler
from bless.config.bless_config import BlessConfig, \
    KMSAUTH_SECTION, \
    KMSAUTH_USEKMSAUTH_OPTION

"""
Usage:

    $ AWS_REGION=us-east-1 gunicorn -w 4 -b 127.0.0.1:4000 server:app

Options:

    $ BLESS_ENTROPY_CHECK=True \
        BLESS_DEPLOY_CONFIG=/path/to/bless_deploy.cfg \
        AWS_REGION=us-east-1 \
        gunicorn -w 4 -b 127.0.0.1:4000 server:app

By default, the server assumes `bless_deploy.cfg` resides at `config/bless_deploy.cfg`.
"""

app = Flask(__name__)


ENTROPY_CHECK = False
if os.environ.get('BLESS_ENTROPY_CHECK', False):
    ENTROPY_CHECK = True


class Context(object):
    """
    Since Bless is meant to run as an AWS Lambda function, we
    need to mock context for things to work properly.
    """
    aws_request_id = str(random.randint(10000,99999))
    invoked_function_arn = str(random.randint(10000,99999))


def ensure_config():
    """
    Check that KMS auth is enabled in the config, raise an error if not.

    Return the path to the config file if all is well.
    """
    region = os.environ['AWS_REGION']
    config_file = os.environ.get(
        'BLESS_DEPLOY_CONFIG', os.path.join(os.path.dirname(__file__), 'config', 'bless_deploy.cfg')
    )

    config = BlessConfig(region, config_file=config_file)
    if not config.get(KMSAUTH_SECTION, KMSAUTH_USEKMSAUTH_OPTION):
        raise ValueError('KMS authentication is required')

    return config_file


@app.route("/_healthcheck", methods=['GET'])
def healthcheck():
    return "ok", 200


@app.route("/bless", methods=['POST'])
def bless():
    if request.is_json:
        data = request.get_json()

        if not data.get('kmsauth_token', False):
            return "Unauthorized", 401

        output = lambda_handler(
            data,
            context=Context,
            entropy_check=ENTROPY_CHECK,
            config_file=ensure_config()
        )

        if data.get('errorType', False):
            return "Bad request", 400

        return json.dumps(output)
    else:
        return "Bad Request", 400
