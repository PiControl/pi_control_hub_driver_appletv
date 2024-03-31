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
from cachetools import TTLCache
from pi_control_hub_driver_api import DeviceCommand
from pi_control_hub_driver_api import DeviceNotFoundException
import pyatv
from pyatv.storage.file_storage import FileStorage

from . import icons

device_cache = TTLCache(20, ttl=1200)


async def __execute_while_connected(device_id: str, storage: FileStorage, operation: Callable):
    loop = asyncio.get_event_loop()
    apple_tv_device = None
    atv = None
    if device_id in device_cache:
        apple_tv_device = device_cache[device_id]
    else:
        devices = await pyatv.scan(identifier=device_id, loop=loop)
        if not devices:
            raise DeviceNotFoundException(device_id=device_id)
        apple_tv_device = devices[0]
        device_cache[device_id] = apple_tv_device
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

async def up(device_id: str, storage: FileStorage):
    async def __up(atv):
        await atv.remote_control.up()

    await __execute_while_connected(device_id, storage, __up)


async def right(device_id: str, storage: FileStorage):
    async def __right(atv):
        await atv.remote_control.right()

    await __execute_while_connected(device_id, storage, __right)


async def down(device_id: str, storage: FileStorage):
    async def __down(atv):
        await atv.remote_control.down()

    await __execute_while_connected(device_id, storage, __down)


async def left(device_id: str, storage: FileStorage):
    async def __left(atv):
        await atv.remote_control.left()

    await __execute_while_connected(device_id,storage,  __left)


async def select(device_id: str, storage: FileStorage):
    async def __select(atv):
        await atv.remote_control.select()

    await __execute_while_connected(device_id, storage, __select)


async def play_pause(device_id: str, storage: FileStorage):
    async def __play_pause(atv):
        await atv.remote_control.play_pause()

    await __execute_while_connected(device_id, storage, __play_pause)


async def back(device_id: str, storage: FileStorage):
    async def __back(atv):
        await atv.remote_control.menu()

    await __execute_while_connected(device_id, storage, __back)


async def volume_up(device_id: str, storage: FileStorage):
    async def __volume_up(atv):
        await atv.audio.volume_up()

    await __execute_while_connected(device_id, storage, __volume_up)


async def volume_down(device_id: str, storage: FileStorage):
    async def __volume_down(atv):
        await atv.audio.volume_down()

    await __execute_while_connected(device_id, storage, __volume_down)


async def home(device_id: str, storage: FileStorage):
    async def __home(atv):
        await atv.remote_control.home()

    await __execute_while_connected(device_id, storage, __home)


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
UP = 3
RIGHT = 4
DOWN = 5
LEFT = 6
SELECT = 7
PLAY_PAUSE = 8
BACK = 9
VOLUME_UP = 10
VOLUME_DOWN = 11
HOME = 12


#### Create commands
def create_commands(device_id: str, storage: FileStorage) -> List[DeviceCommand]:
    return [
        AppleTvDeviceCommand(TURN_ON, "On", icons.turn_on(), device_id, storage, turn_on),
        AppleTvDeviceCommand(TURN_OFF, "Off", icons.turn_off(), device_id, storage, turn_off),

        AppleTvDeviceCommand(UP, "Up", icons.up(), device_id, storage, up),
        AppleTvDeviceCommand(RIGHT, "Right", icons.right(), device_id, storage, right),
        AppleTvDeviceCommand(DOWN, "Down", icons.down(), device_id, storage, down),
        AppleTvDeviceCommand(LEFT, "Left", icons.left(), device_id, storage, left),
        AppleTvDeviceCommand(SELECT, "Select", icons.ok(), device_id, storage, select),
        AppleTvDeviceCommand(PLAY_PAUSE, "Play/Pause", icons.play_pause(), device_id, storage, play_pause),
        AppleTvDeviceCommand(BACK, "Back", icons.back(), device_id, storage, back),
        AppleTvDeviceCommand(VOLUME_UP, "Volume +", icons.volume_up(), device_id, storage, volume_up),
        AppleTvDeviceCommand(VOLUME_DOWN, "Volume -", icons.volume_down(), device_id, storage, volume_down),
        AppleTvDeviceCommand(HOME, "Home", icons.home(), device_id, storage, home),
    ]
