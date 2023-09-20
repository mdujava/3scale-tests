"""
Conftest for the jaeger tests
"""

from weakget import weakget

from testsuite.jaeger import Jaeger

import pytest

@pytest.fixture(scope="module")
def jaeger(testconfig, tools):
    """
    Returns the Jaeger client class used to communicate with jaeger
    configured based on the values from testconfig
    """

    url = weakget(testconfig)["fixtures"]["jaeger"]["url"] % tools["jaeger"]
    a = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return Jaeger(url, testconfig["fixtures"]["jaeger"]["config"], testconfig["ssl_verify"])


@pytest.fixture(scope="module")
def jaeger_service_name(staging_gateway, jaeger):
    """
    Deploys apicast gateway configured with jaeger.
    """
    return staging_gateway.connect_open_telemetry(jaeger)
