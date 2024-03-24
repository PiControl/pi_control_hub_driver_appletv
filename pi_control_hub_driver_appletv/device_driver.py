"""
   Copyright 2024 Thomas Bonk

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import List, Tuple
from uuid import UUID
from pi_control_hub_driver_api import DeviceInfo, AuthenticationMethod, DeviceDriver, DeviceDriverDescriptor

from . import __version__


class AppleTvDeviceDriverDescriptor(DeviceDriverDescriptor):
    """Apple TV device driver descriptor"""

    def __init__(self):
        DeviceDriverDescriptor.__init__(
            self,
            UUID("9a5785fd-69c9-426b-85e0-c860498757bb"), # driver id
            "AppleTV",                                    # display name
            "PiControl Hub driver for AppleTVs",          # description
        )

    def get_devices(self) -> List[DeviceInfo]:
        """Returns a list with the available device instances."""
        return []

    @property
    def authentication_method(self) -> AuthenticationMethod:
        """The authentication method that is required when pairing a device."""
        return AuthenticationMethod.PIN

    @property
    def requires_pairing(self) -> bool:
        """This flag determines whether pairing is required to communicate with this device."""
        return True

    def start_pairing(self, device_info: DeviceInfo, remote_name: str) -> Tuple[str, bool]:
        """Start the pairing process with the given device.

        Parameters
        ----------
        device_info : DeviceInfo
            The device to pair with.
        remote_name : str
            The name of the remote that will control this device.

        Returns
        -------
        A tuple consisting of a pairing request ID and a flag that determines whether the device
        provides a PIN.
        """
        return "", False

    def finalize_pairing(self, pairing_request: str, credentials: str, device_provides_pin: bool) -> bool:
        """Finalize the pairing process

        Parameters
        ----------
        pairing_request : str
            The pairing request ID returns by ``start_pairing``
        device_provides_pin : bool
            The flag that determines whether the device provides a PIN.
        """
        return False

    def create_device_instance(self, device_id: str) -> DeviceDriver:
        """Create a device driver instance for the device with the given ID.

        Parameters
        ----------
        device_id : str
            The ID of the device.

        Returns
        -------
        The instance of the device driver or None in case of an error.
        """
        return None


def get_driver_descriptor() -> DeviceDriverDescriptor:
    """This function returns an instance of the device-specific DeviceDriverDescriptor.

    Returns
    -------
    `AppleTvDeviceDriverDescriptor`: An instance of the DeviceDriverDescriptor.
    """
    return AppleTvDeviceDriverDescriptor()
