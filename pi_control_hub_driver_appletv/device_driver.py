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

import asyncio
import uuid
import os
import pyatv
from pyatv.storage.file_storage import FileStorage
import nest_asyncio

from cachetools import TTLCache

from pi_control_hub_driver_api import DeviceInfo
from pi_control_hub_driver_api import AuthenticationMethod
from pi_control_hub_driver_api import DeviceCommand
from pi_control_hub_driver_api import DeviceDriver
from pi_control_hub_driver_api import DeviceDriverDescriptor
from pi_control_hub_driver_api import DeviceDriverException
from pi_control_hub_driver_api import DeviceNotFoundException
from pi_control_hub_driver_api import CommandNotFoundException

from . import __version__

nest_asyncio.apply()

from .commands import BACK, DOWN, HOME, LEFT, PLAY_PAUSE, RIGHT, SELECT, TURN_OFF, TURN_ON, UP, VOLUME_DOWN, VOLUME_UP, create_commands
from .synchronized import synchronized


class PyAtvStorage:
    __global_storage = None

    @staticmethod
    def get_storage() -> FileStorage:
        if PyAtvStorage.__global_storage is None:
            PyAtvStorage.__global_storage = FileStorage(filename=os.path.join(DeviceDriverDescriptor.get_config_path(), "appletv.conf"), loop=asyncio.get_event_loop())
            synchronized(PyAtvStorage.__global_storage.load())
        return PyAtvStorage.__global_storage


class AppleTvDeviceDriver(DeviceDriver):
    """The driver that communicates with a AppleTV."""
    def __init__(self, device_info: DeviceInfo):
        self._device_info = device_info
        self._commands = create_commands(device_info.device_id, PyAtvStorage.get_storage())

    @property
    def name(self) -> str:
        """The device name."""
        return self._device_info.name

    @property
    def device_id(self) -> str:
        """The device ID."""
        return self._device_info.device_id

    def get_commands(self) -> List[DeviceCommand]:
        """Return the commands that are supported by this device.

        Returns
        -------
        The commands that are supported by this device.

        Raises
        ------
        `DeviceDriverException` in case of an error.
        """
        return self._commands

    def get_command(self, cmd_id: int) -> DeviceCommand:
        """Return the command with the given ID.

        Parameters
        ----------
        cmd_id : int
            The numeric ID of the command.

        Returns
        -------
        The command for the ID.

        Raises
        ------
        `CommandNotFoundException` if the command is not known.

        `DeviceDriverException` in case of an other error.
        """
        result = list(filter(lambda c: c.id == cmd_id, self.get_commands()))
        if len(result) > 0:
            return result[0]
        raise CommandNotFoundException(self.name, cmd_id)

    @property
    def remote_layout_size(self) -> Tuple[int, int]:
        """
        The size of the remote layout.

        Returns
        -------
        A tuple with the width and height of the layout
        """
        return 3, 6

    @property
    def remote_layout(self) -> List[List[int]]:
        """
        The layout of the remote.

        Returns
        -------
        The layout as a list of columns.
        """
        return [
            [TURN_ON, -1, TURN_OFF],
            [-1, UP, -1],
            [LEFT, SELECT, RIGHT],
            [-1, DOWN, -1],
            [PLAY_PAUSE, BACK, HOME],
            [VOLUME_DOWN, -1, VOLUME_UP],
        ]

    def execute(self, command: DeviceCommand):
        """
        Executes the given command.

        Parameters
        ----------
        command : DeviceCommand
            The command that shall be executed

        Raises
        ------
        `DeviceCommandException` in case of an error while executing the command.
        """
        command.execute()

    @property
    def is_device_ready(self) -> bool:
        """
        A flag the determines whether the device is ready.

        Returns
        -------
        true if the device is ready, otherwise false.
        """
        return True


class AppleTvDeviceDriverDescriptor(DeviceDriverDescriptor):
    """Apple TV device driver descriptor"""

    pairing_requests_cache = None

    def __init__(self):
        if AppleTvDeviceDriverDescriptor.pairing_requests_cache is None:
            AppleTvDeviceDriverDescriptor.pairing_requests_cache = TTLCache(maxsize=10, ttl=300)
        DeviceDriverDescriptor.__init__(
            self,
            UUID("9a5785fd-69c9-426b-85e0-c860498757bb"),   # driver id
            "AppleTV",                                      # display name
            "PiControl Hub driver for controling AppleTVs", # description
        )

    def get_devices(self) -> List[DeviceInfo]:
        """Returns a list with the available device instances."""
        raw_devices = synchronized(pyatv.scan(loop=asyncio.get_event_loop()))
        return list(
            map(
                lambda d: DeviceInfo(name=d.name, device_id=d.identifier),
                list(
                    filter(
                        lambda d: d.device_info.raw_model.startswith('AppleTV'), raw_devices))))

    def get_device(self, device_id: str) -> DeviceInfo:
        loop = asyncio.get_event_loop()
        devices = synchronized(pyatv.scan(identifier=device_id, loop=loop))
        if not devices:
            raise DeviceNotFoundException(device_id=device_id)
        return DeviceInfo(devices[0].name, devices[0].identifier)

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
        provides a PIN. If the device is not found (None, False) is returned.
        """
        loop = asyncio.get_event_loop()
        devices = synchronized(pyatv.scan(identifier=device_info.device_id, loop=loop))
        if not devices:
            return None, False

        pyatv_storage = PyAtvStorage.get_storage()
        apple_tv_device = devices[0]
        pairing_handler = synchronized(
            pyatv.pair(
                config=apple_tv_device,
                protocol=pyatv.Protocol.Companion,
                loop=loop,
                storage=pyatv_storage,
                name=remote_name))
        synchronized(pairing_handler.begin())
        synchronized(pyatv_storage.save())
        pairing_request = str(uuid.uuid4())
        AppleTvDeviceDriverDescriptor.pairing_requests_cache[pairing_request] = pairing_handler

        return str(pairing_request), pairing_handler.device_provides_pin

    def finalize_pairing(self, pairing_request: str, credentials: str, device_provides_pin: bool) -> bool:
        """Finalize the pairing process

        Parameters
        ----------
        pairing_request : str
            The pairing request ID returns by ``start_pairing``
        device_provides_pin : bool
            The flag that determines whether the device provides a PIN.
        """
        if not pairing_request in AppleTvDeviceDriverDescriptor.pairing_requests_cache:
            raise DeviceDriverException(f"The pairing request ID '{pairing_request}' is not found.")
        pyatv_storage = PyAtvStorage.get_storage()
        pairing_handler: pyatv.interface.PairingHandler = AppleTvDeviceDriverDescriptor.pairing_requests_cache[pairing_request]
        pairing_handler.pin(credentials)
        synchronized(pairing_handler.finish())
        synchronized(pairing_handler.close())
        synchronized(pyatv_storage.save())
        return pairing_handler.has_paired

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
        return AppleTvDeviceDriver(self.get_device(device_id))


def get_driver_descriptor() -> DeviceDriverDescriptor:
    """This function returns an instance of the device-specific DeviceDriverDescriptor.

    Returns
    -------
    `AppleTvDeviceDriverDescriptor`: An instance of the DeviceDriverDescriptor.
    """
    return AppleTvDeviceDriverDescriptor()
