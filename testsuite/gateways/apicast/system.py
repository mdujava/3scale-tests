"""System Apicast that comes deployed with 3scale"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from testsuite.gateways.gateways import AbstractApicast, Capability, GatewayRequirements
from testsuite.openshift.env import Environ

if TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from testsuite.openshift.client import OpenShiftClient


class SystemApicastRequirements(GatewayRequirements, ABC):
    """Requirements for SystemApicast"""
    @property
    @abstractmethod
    def staging_deployment(self) -> str:
        """Returns staging deployment"""

    @property
    @abstractmethod
    def production_deployment(self) -> str:
        """Returns production deployment"""


class SystemApicast(AbstractApicast):
    """Apicast that is deployed with 3scale"""

    CAPABILITIES = [Capability.SAME_CLUSTER,
                    Capability.CUSTOM_ENVIRONMENT,
                    Capability.APICAST,
                    Capability.PRODUCTION_GATEWAY,
                    Capability.STANDARD_GATEWAY,
                    Capability.LOGS]

    def __init__(self, requirements: SystemApicastRequirements):
        if requirements.staging:
            self.deployment = requirements.staging_deployment
        else:
            self.deployment = requirements.production_deployment
        self.openshift: "OpenShiftClient" = requirements.current_openshift
        self.name = self.deployment
        self.options = requirements

    @property
    def environ(self) -> Environ:
        return self.openshift.environ(self.deployment)

    def reload(self):
        self.openshift.rollout(f"dc/{self.deployment}")

    def get_logs(self):
        return self.openshift.get_logs(self.deployment)
