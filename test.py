from Application.VideoReader import VideoReader
from Application.Config import Config
import os

fileName = "out.mp4"
dirName = os.path.join(os.path.dirname(__file__), "generate test footage")

config = {}
config["inputPath"] = os.path.join(dirName, fileName)
config["videoBufferLength"] = 100

with VideoReader(config) as reader:
    while not reader.videoEnded():
        framenumber, frame = reader.pop()
        print(framenumber)
