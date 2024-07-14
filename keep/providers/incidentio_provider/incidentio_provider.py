"""
IncidentioProvider is a class that allows to get all incidents as well query specific incidents in Incidentio.
"""

import dataclasses
from typing import List
from urllib.parse import urlencode, urljoin

import pydantic
import requests

from keep.api.models.alert import AlertDto, AlertSeverity, AlertStatus
from keep.contextmanager.contextmanager import ContextManager
from keep.providers.base.base_provider import BaseProvider
from keep.providers.models.provider_config import ProviderConfig, ProviderScope


class ResourceAlreadyExists(Exception):
    def __init__(self, *args):
        super().__init__(*args)


@pydantic.dataclasses.dataclass
class IncidentioProviderAuthConfig:
    """
    Incidentio authentication configuration.
    """
    incidentIoApiKey: str = dataclasses.field(
        metadata={
            "required": True,
            "description": "IncidentIO's API_KEY",
            "hint": "API KEY for incident.io",
            "sensitive": True,
        },
    )


class IncidentioProvider(BaseProvider):
    """Receive Incidents from Incidentio."""

    PROVIDER_SCOPES = [
        ProviderScope(
            name="authenticated",
            description="User is Authenticated",
            mandatory=True,
            alias="authenticated",
        ),
        ProviderScope(
            name="read_access",
            description="User has read access",
            mandatory=True,
            alias="can_read",
        )
    ]

    SEVERITIES_MAP = {
        "warning": AlertSeverity.WARNING,
        "high": AlertSeverity.HIGH,
        "info": AlertSeverity.INFO,
        "critical": AlertSeverity.CRITICAL,
        "low": AlertSeverity.LOW
    }

    STATUS_MAP = {
        "triage": AlertStatus.ACKNOWLEDGED,
        "declined": AlertStatus.SUPPRESSED,
        "merged": AlertStatus.RESOLVED,
        "canceled": AlertStatus.SUPPRESSED,
        "live": AlertStatus.FIRING,
        "learning": AlertStatus.PENDING,
        "closed": AlertStatus.RESOLVED,
        "paused": AlertStatus.SUPPRESSED
    }

    def __init__(
            self, context_manager: ContextManager, provider_id: str, config: ProviderConfig
    ):
        super().__init__(context_manager, provider_id, config)

    def dispose(self):
        """
        Dispose the provider.
        """
        pass

    def validate_config(self):
        """
        Validates required configuration for Incidentio provider.
        """
        self.authentication_config = IncidentioProviderAuthConfig(
            **self.config.authentication
        )

    def __get_url(self, paths: List[str] = [], query_params: dict = None, **kwargs):
        """
        Helper method to build the url for Incidentio api requests.

        Example:

        paths = ["issue", "createmeta"]
        query_params = {"projectKeys": "key1"}
        url = __get_url("test", paths, query_params)

        # url = https://incidentio.com/api/2/issue/createmeta?projectKeys=key1
        """

        url = urljoin(
            f"https://api.incident.io/v2",
            "/".join(str(path) for path in paths),
        )

        # add query params
        if query_params:
            url = f"{url}?{urlencode(query_params)}"

        return url

    def __get_headers(self):
        """
        Building the headers for api requests
        """
        return {
            'Authorization': f'Bearer {self.authentication_config.incidentIoApiKey}',
        }

    def validate_scopes(self) -> dict[str, bool | str]:
        authenticated = False
        read_access = False
        self.logger.info("Validating IncidentIO scopes...")
        try:
            response = requests.get(
                url=self.__get_url(paths=["incidents"]),
                timeout=10,
                headers=self.__get_headers(),
            )
        except Exception as e:
            self.logger.error("Error getting IncidentIO scopes:", extra={"exception": str(e)})
        else:
            if response.ok:
                res = response.json()
                self.logger.info("Successfully retrieved IncidentIO scopes...", extra={"response": res})
                authenticated = True
                read_access = True
            else:
                self.logger.info("Error getting IncidentIO scopes:", extra={"response": response.text})
        finally:
            return {
                "authenticated": authenticated,
                "read_access": read_access,
            }

    def _query(self, incident_id, **kwargs) -> AlertDto:
        """query IncidentIO Incident"""
        self.logger.info("Querying IncidentIO incident",
                         extra={
                             "incident_id": incident_id,
                             **kwargs,
                         }, )
        try:
            response = requests.get(
                url=self.__get_url(paths=["incidents", incident_id]),
                headers=self.__get_headers(),
            )
        except Exception as e:
            self.logger.error("Error while fetching Incident",
                              extra={"incident_id": incident_id, "kwargs": kwargs, "exception": str(e)})
            raise e
        else:
            if response.ok:
                res = response.json()
                return self.__map_alert_to_AlertDTO({"event": res})
            else:
                self.logger.error("Error while fetching Incident",
                                  extra={"incident_id": incident_id, "kwargs": kwargs, "res": response.text})

    def _get_alerts(self) -> list[AlertDto]:
        alerts = []
        next_page = None

        while True:
            try:
                params = {'page_size': 100}
                if next_page:
                    params['after'] = next_page

                response = requests.get(self.__get_url(paths=[]), headers=self.__get_headers(), params=params,
                                        timeout=15)
                response.raise_for_status()
            except requests.RequestException as e:
                self.logger.error("Error getting IncidentIO scopes:", extra={"exception": str(e)})
                raise e
            else:
                data = response.json()
                try:
                    for incident in data.get('incidents', []):
                        alerts.append(
                            self.__map_alert_to_AlertDTO(incident)
                        )
                except Exception as e:
                    self.logger.error("Error while mapping incidents to AlertDTO", extra={"exception": str(e)})
                    raise e
                pagination_meta = data.get('pagination_meta', {})
                next_page = pagination_meta.get('after')

                if not next_page:
                    break

        return alerts

    def __map_alert_to_AlertDTO(self, incident) -> AlertDto:
        return AlertDto(
            id=incident['id'],
            fingerprint=incident['id'],
            name=incident['name'],
            status=IncidentioProvider.STATUS_MAP[incident['incident_status']["category"]],
            severity=IncidentioProvider.SEVERITIES_MAP[
                incident.get("severity", {}).get("name", "minor")],
            lastReceived=incident.get('created_at'),
            description=incident.get('summary', ""),
            apiKeyRef=incident["creator"]["api_key"]["id"],
            assignee=", ".join(
                assignment["assignee"]["name"] for assignment in
                incident["incident_role_assignments"]),
            url=incident.get("permalink", "https://app.incident.io/")
        )