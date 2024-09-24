import asyncio
import os
import sys
import threading
import re
import pygame
from dotenv import get_key
from AudioAI import AudioAI
from TextAI import TextAI
from IRacing import IRacing
from MainPresenter import MainPresenter
from TextAI import TextAI
from UI import UI

if __name__ == "__main__":
    ir = IRacing()
    audio_AI = AudioAI()
    text_AI = TextAI()
    ui = UI()
    presenter = MainPresenter(ui, audio_AI, text_AI, ir)