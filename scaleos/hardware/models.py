# Create your models here.
import logging

import requests
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin

logger = logging.getLogger(__name__)


class Network(NameField, AdminLinkMixin, PublicKeyField, LogInfoFields):
    tailscale_organization_name = models.CharField(
        default="",
        blank=True,
        help_text="https://login.tailscale.com/admin/settings/general",
    )
    tailscale_api_key = models.CharField(
        default="",
        blank=True,
        help_text="https://login.tailscale.com/admin/settings/keys",
    )

    class Meta:
        verbose_name = _("network")
        verbose_name_plural = _("networks")

    def sync_tailscale(self):
        """
        tailscale example
        {
            "addresses": [
                "100.794",
                "fd7a:115c:a1e0:ab12:4843:cd96:6246:95e"
            ],
            "authorized": true,
            "blocksIncomingConnections": false,
            "clientVersion": "1.40.0-t105be684d-g4c70014a4",
            "created": "2023-03-21T19:35:23Z",
            "expires": "2023-09-17T19:35:23Z",
            "hostname": "acepc",
            "id": "16909...3489",
            "isExternal": false,
            "keyExpiryDisabled": true,
            "lastSeen": "2023-05-08T16:23:56Z",
            "machineKey": "mkey:7bfaef7ec57cb...e27e5411aa591cdbd347f",
            "name": "acepc.d....s.net",
            "nodeId": "nUV...NTRL",
            "nodeKey": "nodekey:5adb96551c0f2c...1f58102560959",
            "os": "linux",
            "tailnetLockError": "",
            "tailnetLockKey": "nlpub:5c97fe...1a37af6d6467e44e95465236212df8dc41",
            "updateAvailable": true,
            "user": "mr@ail.com"
        },
        """

        # https://login.tailscale.com/admin/settings/general
        organization_name = self.tailscale_organization_name
        api_key = self.tailscale_api_key
        endpoint = (
            f"https://api.tailscale.com/api/v2/tailnet/{organization_name}/devices"
        )
        headers = {"Authorization": f"Bearer {api_key}"}
        devices = requests.get(
            endpoint,
            headers=headers,
            timeout=30,
        )

        logger.debug("Devices: %s", devices.text)
        devices = devices.json()
        response_msg = devices.get("message", None)
        if response_msg:
            raise NotImplementedError(response_msg)
            logger.warning()
        for device in devices["devices"]:
            node_id = device["nodeId"]
            name = device["name"]
            computer, computer_created = Computer.objects.get_or_create(
                node_id=node_id,
                name=name,
                network_id=self.id,
            )
            computer.ip_addresses = device["addresses"]
            computer.last_seen = device["lastSeen"]
            computer.created = device["created"]
            computer.expires = device["expires"]
            computer.client_version = device["clientVersion"]
            computer.update_available = device["updateAvailable"]
            computer.is_active = True
            computer.hostname = device["hostname"]
            computer.save()


# Create your models here.
class Device(
    PolymorphicModel,
    NameField,
    AdminLinkMixin,
    PublicKeyField,
    LogInfoFields,
):
    organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_(
            "organization",
        ),
        related_name="devices",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")


class Computer(Device):
    network = models.ForeignKey(
        Network,
        verbose_name=_(
            "network",
        ),
        related_name="devices",
        on_delete=models.CASCADE,
        null=True,
    )
    # Tailscale Info
    expires = models.DateTimeField(verbose_name=_("expires"), null=True, editable=False)
    last_seen = models.DateTimeField(
        verbose_name=_("last seen"),
        null=True,
        editable=False,
    )
    client_version = models.CharField(
        verbose_name=_("client version"),
        default="",
        editable=False,
    )
    update_available = models.BooleanField(
        verbose_name=_("update available"),
        default=False,
    )
    hostname = models.CharField(verbose_name=_("hostname"), default="", editable=False)
    is_active = models.BooleanField(verbose_name=_("is active"), default=False)
    node_id = models.CharField(
        verbose_name=_("node id"),
        max_length=30,
        default="",
        editable=False,
    )
    created = models.DateTimeField(verbose_name=_("created"), null=True, editable=False)
    ip_addresses = models.CharField(
        verbose_name=_("ip addresses"),
        editable=False,
        default="",
    )
    tailscale_ipv4 = models.GenericIPAddressField(null=True, editable=False)

    class Meta:
        verbose_name = _("computer")
        verbose_name_plural = _("computers")
