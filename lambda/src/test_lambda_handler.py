import json

import pytest

from battery_status import lambda_handler


@pytest.fixture
def lambda_context():
    return {}


@pytest.fixture
def test_case_1():
    return {"device": "device_1", "payload": "F1E6E63676C75000"}


@pytest.fixture
def test_case_2():
    return {"device": "device_2", "payload": "9164293726C85400"}


@pytest.fixture
def test_case_3():
    return {"device": "device_3", "payload": "6188293726C75C00"}


def test_lambda_handler_bad_input(lambda_context):
    bad_input = {"key_1": "value"}
    response = lambda_handler(bad_input, lambda_context)

    assert response["statusCode"] == 400

def test_lambda_handler_1(test_case_1, lambda_context):
    expected = {
        "device": "device_1",
        "time": 1668181615,
        "state": "error",
        "state_of_charge": 99.5,
        "temperature": 20.0
    }
    response = lambda_handler(test_case_1, lambda_context)

    assert response["statusCode"] == 200
    assert expected == json.loads(response["body"]["result"])


def test_lambda_handler_2(test_case_2, lambda_context):
    expected = {
        "device": "device_2",
        "time": 1668453961,
        "state": "discharge",
        "state_of_charge": 100.0,
        "temperature": 22.0
    }
    response = lambda_handler(test_case_2, lambda_context)

    assert response["statusCode"] == 200
    assert expected == json.loads(response["body"]["result"])


def test_lambda_handler_3(test_case_3, lambda_context):
    expected = {
        "device": "device_3",
        "time": 1668454534,
        "state": "discharge",
        "state_of_charge": 99.5,
        "temperature": 26.0
    }
    response = lambda_handler(test_case_3, lambda_context)

    assert response["statusCode"] == 200
    assert expected == json.loads(response["body"]["result"])


