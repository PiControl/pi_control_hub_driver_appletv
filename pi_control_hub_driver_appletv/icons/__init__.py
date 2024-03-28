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

import os
import pathlib

__directory = pathlib.Path(__file__).parent.resolve()

def __read_icon(filename: str) -> bytes:
    f = open(os.path.join(__directory, filename), mode="rb")
    data: bytes = f.read()
    f.close
    return data

def back() -> bytes: return __read_icon("back.png")
def down() -> bytes: return __read_icon("down.png")
def home() -> bytes: return __read_icon("home.png")
def left() -> bytes: return __read_icon("left.png")
def mute() -> bytes: return __read_icon("mute.png")
def ok() -> bytes: return __read_icon("ok.png")
def play_pause() -> bytes: return __read_icon("play-pause.png")
def right() -> bytes: return __read_icon("right.png")
def turn_off() -> bytes: return __read_icon("turn-off.png")
def turn_on() -> bytes: return __read_icon("turn-on.png")
def up() -> bytes: return __read_icon("up.png")
def volume_up() -> bytes: return __read_icon("volume-up.png")
def volume_down() -> bytes: return __read_icon("volume-down.png")
