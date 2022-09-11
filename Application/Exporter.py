import pickle
import time
from datetime import datetime

import cv2
import imageio
import imutils
import numpy as np

from Application.VideoReader import VideoReader


class Exporter:
    def __init__(self, config):
        self.footage_path = config["inputPath"]
        self.output_path = config["outputPath"]
        self.resize_width = config["resizeWidth"]
        self.config = config
        print("Exporter initiated")

    def export(self, layers, contours, masks, raw=True, overlayed=True, black_background=False, show_progress=False):
        if raw:
            self.export_raw_data(layers, contours, masks)
        if overlayed:
            self.export_overlayed(layers, black_background, show_progress)
        else:
            self.export_layers(layers)

    def export_layers(self, layers):
        list_of_frames = self.make_list_of_frames(layers)
        with VideoReader(self.config, list_of_frames) as video_reader:
            
            underlay = cv2.VideoCapture(self.footage_path).read()[1]
            underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)

            fps = video_reader.get_fps()
            writer = imageio.get_writer(self.output_path, fps=fps)

            start = time.time()
            for i, layer in enumerate(layers):
                print(f"\r {i}/{len(layers)} {round(i/len(layers)*100,2)}% {round((time.time() - start), 2)}s", end="\r")
                if len(layer.bounds[0]) == 0:
                    continue
                video_reader = VideoReader(self.config)
                list_of_frames = self.make_list_of_frames([layer])
                video_reader.fill_buffer(list_of_frames)
                while not video_reader.video_ended():
                    frame_count, frame = video_reader.pop()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame2 = np.copy(underlay)
                    for (x, y, w, h) in layer.bounds[frame_count - layer.startFrame]:
                        if x is None:
                            continue
                        factor = video_reader.w / self.resize_width
                        x, y, w, h = (int(x * factor), int(y * factor), int(w * factor), int(h * factor))

                        frame2[y : y + h, x : x + w] = np.copy(frame[y : y + h, x : x + w])

                        self.add_timestamp(frame2, video_reader, frame_count, x, y, w, h)
                    writer.append_data(frame2)

            writer.close()

    def export_overlayed(self, layers, black_background=False, show_progress=False):

        list_of_frames = self.make_list_of_frames(layers)
        max_length = self.get_max_length_of_layers(layers)

        with VideoReader(self.config, list_of_frames) as videoReader:
            if black_background:
                underlay = np.zeros(shape=[videoReader.h, videoReader.w, 3], dtype=np.uint8)
            else:
                underlay = cv2.VideoCapture(self.footage_path).read()[1]
                underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)

            frames = []
            for i in range(max_length):
                frames.append(np.copy(underlay))
            fps = videoReader.fps
            while not videoReader.video_ended():
                frame_count, frame = videoReader.pop()
                if frame_count % (60 * fps) == 0:
                    print("Minutes processed: ", frame_count / (60 * fps), end="\r")
                if frame is None:
                    print("ContourExtractor: frame was None")
                    continue

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                for layer in layers:
                    if layer.startFrame <= frame_count and layer.startFrame + len(layer.bounds) > frame_count:
                        for i in range(0, len(layer.bounds[frame_count - layer.startFrame])):
                            try:
                                x, y, w, h = layer.bounds[frame_count - layer.startFrame][i]
                                if None in (x, y, w, h):
                                    break
                                factor = videoReader.w / self.resize_width
                                x, y, w, h = (int(x * factor), int(y * factor), int(w * factor), int(h * factor))

                                mask = self.get_mask(i, frame_count, layer, w, h)
                                background = frames[frame_count - layer.startFrame + layer.exportOffset]
                                self.add_masked_content(frame, x, y, w, h, mask, background)
                                frames[frame_count - layer.startFrame + layer.exportOffset] = np.copy(background)

                                if show_progress:
                                    cv2.imshow("changes x", background)
                                    cv2.waitKey(10) & 0xFF

                                self.add_timestamp(frames[frame_count - layer.startFrame + layer.exportOffset], videoReader, frame_count, x, y, w, h)
                            except:
                                continue

        writer = imageio.get_writer(self.output_path, fps=videoReader.get_fps())
        for frame in frames:
            writer.append_data(frame)

        writer.close()

    def add_masked_content(self, frame, x, y, w, h, mask, background):
        masked_frame = np.copy(
            cv2.bitwise_and(
                background[y : y + h, x : x + w],
                background[y : y + h, x : x + w],
                mask=cv2.bitwise_not(mask),
            )
        )
        background[y : y + h, x : x + w] = cv2.addWeighted(
            masked_frame,
            1,
            np.copy(cv2.bitwise_and(frame[y : y + h, x : x + w], frame[y : y + h, x : x + w], mask=mask)),
            1,
            0,
        )

    def add_timestamp(self, frame, video_reader, frame_count, x, y, w, h):
        time = datetime.fromtimestamp(int(frame_count / video_reader.fps) + video_reader.get_start_time())
        cv2.putText(
            frame,
            f"{time.hour}:{time.minute}:{time.second}",
            (int(x + w / 2), int(y + h / 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

    def get_mask(self, i, frame_count, layer, w, h):
        mask = layer.masks[frame_count - layer.startFrame][i]
        mask = imutils.resize(mask, width=w, height=h + 1)
        mask = np.resize(mask, (h, w))
        mask = cv2.erode(mask, None, iterations=10)
        mask *= 255
        return mask

    def export_raw_data(self, layers, contours, masks):
        with open(self.config["importPath"] + "_layers", "wb+") as file:
            pickle.dump(layers, file)
        with open(self.config["importPath"] + "_contours", "wb+") as file:
            pickle.dump(contours, file)
        with open(self.config["importPath"] + "_masks", "wb+") as file:
            pickle.dump(masks, file)

    def get_max_length_of_layers(self, layers):
        max_length = 0
        for layer in layers:
            if layer.getLength() > max_length:
                max_length = layer.getLength()
        return max_length

    def make_list_of_frames(self, layers):
        """Returns set of all Frames which are relevant to the Layers"""
        frame_numbers = set()
        for layer in layers:
            frame_numbers.update(list(range(layer.startFrame, layer.startFrame + len(layer))))

        return sorted(list(frame_numbers))
