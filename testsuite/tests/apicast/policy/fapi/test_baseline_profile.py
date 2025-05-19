"""
Test that fapi policy fulfills Baseline profile specification.
"""
from uuid import UUID
import re
import pytest

from testsuite import rawobj
from testsuite.utils import blame
from .headers import Headers


@pytest.fixture(scope="module")
def policy_settings():
    """Set policy settings"""

    return rawobj.PolicyConfig("fapi", {})


@pytest.fixture()
def custom_id(request):
    """ FAPI id to be used in a request """
    return blame(request, "fapi-id", 10)


@pytest.fixture(scope="module")
def fapi_service(service):
    """
    todo

    policy order:
        3scale APIcast
        Fapi
        Logging
    """
    fapi_policy = rawobj.PolicyConfig("fapi", configuration = {
        "validate_x_fapi_customer_ip_address": True
      })
    logging_policy = rawobj.PolicyConfig("logging", {
        "enable_access_logs": False,
        "custom_logging": 
            f'{{{{req.headers.{Headers.TRANSACTION_ID.value}}}}}#{{{{resp.headers.{Headers.TRANSACTION_ID.value}}}}}'}
        )
    service.proxy.list().policies.insert(1, fapi_policy)
    service.proxy.list().policies.insert(2, logging_policy)
    return service


# @pytest.fixture()
# def the_client(request, api_client, prod_client):
#     """Set policy settings"""
#     if request.param == "api_client":
#         return api_client
#     if request.param == "prod_client":
#         return prod_client


# pylint: disable=unused-argument
def test_x_fapi_header_provided(custom_id, staging_gateway, api_client, application, fapi_service):
    """
        Test that requests on product with fapi policy returns correct x-fapi-transaction-id header
    Test:
        - Create product with fapi policy via API
        - Send http GET request to endpoint / with header "x-fapi-transaction-id: anything"
        - assert that response has status code 200 and has header "x-fapi-transaction-id: anything"
        - Send another GET request to endpoint / without header "x-fapi-transaction-id"
        - assert that response has status code 200
        - assert that response has header "x-fapi-transaction-id: uuid", where uuid is
        valid uuid version 4 specified in RFC 4122  todo prepsat
    """

    client = api_client()
    trans_id = custom_id  # str(uuid4())
    result = client.get("/", headers = {Headers.TRANSACTION_ID.value: trans_id})
    fapi_id = result.headers.get(Headers.TRANSACTION_ID.value)
    assert result.status_code == 200
    assert fapi_id is not None
    assert fapi_id == trans_id

    logs = staging_gateway.get_logs()
    match = re.search(f"{custom_id}#{custom_id}", logs, re.MULTILINE)  #TODO: add response
    assert match is not None


# pylint: disable=unused-argument
def test_x_fapi_header_created (staging_gateway, api_client, application, fapi_service):  #TODO: parametrize gateway
    """
        todo

    """
    client = api_client()
    result = client.get("/")
    fapi_id = result.headers.get(Headers.TRANSACTION_ID.value)
    assert result.status_code == 200
    assert fapi_id is not None
    assert UUID(fapi_id).variant == 'specified in RFC 4122'
    assert UUID(fapi_id).version == 4

    logs = staging_gateway.get_logs()
    match = re.search(f"#{fapi_id}", logs, re.MULTILINE)  # todo
    assert match is not None


@pytest.mark.parametrize(
    "ip, ok",
    [
        ("198.51.100.119", True),
        ("2001:db8::1:0", True),
        ("anything", False)
    ],
)
# pylint: disable=unused-argument
def test_x_fapi_customer_ip(ip, ok, api_client, application, fapi_service):
    client = api_client()
    resp = client.get("/", headers={Headers.CUSTOMER_IP_ADDR.value: ip})
    assert resp.ok == ok
