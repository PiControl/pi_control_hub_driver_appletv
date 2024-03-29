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

import asyncio
from typing import Callable, List
from pi_control_hub_driver_api import DeviceCommand
from pi_control_hub_driver_api import DeviceNotFoundException
import pyatv
from pyatv.storage.file_storage import FileStorage

from . import icons


async def __execute_while_connected(device_id: str, storage: FileStorage, operation: Callable):
    loop = asyncio.get_event_loop()
    devices = await pyatv.scan(identifier=device_id, loop=loop)

    if not devices:
        raise DeviceNotFoundException(device_id=device_id)

    apple_tv_device = devices[0]
    atv = await pyatv.connect(apple_tv_device, loop=loop, storage=storage)
    await operation(atv)
    await asyncio.gather(*atv.close())


async def turn_off(device_id: str, storage: FileStorage):
    async def __turn_off(atv):
        await atv.power.turn_off()

    await __execute_while_connected(device_id, storage, __turn_off)


async def turn_on(device_id: str, storage: FileStorage):
    async def __turn_on(atv):
        await atv.power.turn_on()

    await __execute_while_connected(device_id, storage, __turn_on)


class AppleTvDeviceCommand(DeviceCommand):
    def __init__(
            self,
            cmd_id: int,
            title: str,
            icon: bytes,
            device_id: str,
            storage: FileStorage,
            callback: Callable[[str, FileStorage], None]):
        DeviceCommand.__init__(self, cmd_id=cmd_id, title=title, icon=icon)
        self._storage = storage
        self._device_id = device_id
        self._callback = callback

    async def execute(self):
        """
        Execute the command. This method must be implemented by the specific command.

        Raises
        ------
        `DeviceCommandException` in case of an error while executing the command.
        """
        await self._callback(self._device_id, self._storage)

#### Command IDs
TURN_ON = 1
TURN_OFF = 2

#### Create commands
def create_commands(device_id: str, storage: FileStorage) -> List[DeviceCommand]:
    return [
        AppleTvDeviceCommand(TURN_ON, "On", icons.turn_on(), device_id, storage, turn_on),
        AppleTvDeviceCommand(TURN_OFF, "Off", icons.turn_off(), device_id, storage, turn_off),
    ]