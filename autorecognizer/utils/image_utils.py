# noinspection PyPackageRequirements
import cv2
import math
import os
# noinspection PyPackageRequirements
import time
from time import gmtime, strftime
from autorecognizer.models import Camera, ParkingSpot, Graph
import threading
from autorecognizer.utils.classify_image import classify
import numpy as np
# noinspection PyPackageRequirements
# import tensorflow as tf
# import urllib.request as urllib

PROJECT_ROOT = \
    os.path.abspath(
        os.path.dirname(
            os.path.abspath(
                os.path.dirname(
                    os.path.abspath(
                        os.path.dirname(
                            os.path.abspath(__file__)))))))


def rotate_image(image, parking_spot):
    rows, cols, channels = image.shape
    m = cv2.getRotationMatrix2D((parking_spot.leftUpperY, parking_spot.leftUpperX), parking_spot.rotation, 1)
    return cv2.warpAffine(image, m, (cols, rows))


def rotate_cords(image, parking_spot):
    height, width, channels = image.shape
    mat = create_mat(height, width)
    mat[parking_spot.rightLowerX][parking_spot.rightLowerY] = 1
    m = cv2.getRotationMatrix2D((parking_spot.leftUpperY, parking_spot.leftUpperX), parking_spot.rotation, 1)
    rotated = cv2.warpAffine(mat, m, (width, height))
    parking_spot.rotatedCordX, parking_spot.rotatedCordY = find_marked_coordinate(rotated)
    return parking_spot


def create_mat(cols, rows):
    return np.zeros((cols, rows))


def find_marked_coordinate(mat):
    rows, cols = mat.shape
    for x in range(0, rows):
        for y in range(0, cols):
            if mat[x][y] != 0:
                return x, y
    return rows, cols


def cut_from_image(image, x1, y1, x2, y2):
    return image[int(x1):int(x2), int(y1):int(y2)]


def get_angle(parking_spot):
    side = 1
    a = parking_spot.leftLowerX - parking_spot.leftUpperX
    if parking_spot.leftUpperY >= parking_spot.leftLowerY:
        b = parking_spot.leftUpperY - parking_spot.leftLowerY
    else:
        b = parking_spot.leftLowerY - parking_spot.leftUpperY
        side = -1
    c = math.hypot(a, b)
    angle = math.degrees(math.asin(b / c)) * side
    return angle


def save_parking_spot(parking_spot, img):
    if parking_spot.rotation is None:
        parking_spot.rotation = get_angle(parking_spot)
    if parking_spot.rotatedCordX is None:
        parking_spot = rotate_cords(img, parking_spot)
    # noinspection PyUnresolvedReferences
    parking_spot.save()


def save_graph(graph_path, labels_path):
    Graph(path=graph_path, labelsPath=labels_path).save()


def get_frame_from_stream(camera):
    if camera.isMjpeg:
        # return get_frame_mjpg(camera)
        return None
    else:
        return get_frame_non_mjpg(camera)


# def get_frame_mjpg(camera):
#     stream = urllib.urlopen(camera.streamUrl)
#     bytes = bytes()
#     while True:
#         bytes += stream.read(1024)
#         a = bytes.find(b'\xff\xd8')
#         b = bytes.find(b'\xff\xd9')
#         if a != -1 and b != -1:
#             jpg = bytes[a:b + 2]
#             bytes = bytes[b + 2:]
#             return cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)


# noinspection PyArgumentList
def get_frame_non_mjpg(camera):
    cap = cv2.VideoCapture(camera.streamUrl)
    limit = 100
    i = 0
    while not cap.isOpened():
        print("FAILED: Attempt to load video stream: " + camera.streamUrl)
        cap = cv2.VideoCapture(camera.streamUrl)
        time.sleep(1)
        if limit == i:
            return None
        i += 1

    while True:
        flag, frame = cap.read()
        if flag:
            cap.release()
            return frame
        else:
            print("FAILED: Attempt to load frame from video stream: " + camera.streamUrl)


def create_sample_data_from_stream(camera, video_loc=os.path.join(PROJECT_ROOT, 'media', 'tmp', 'new_data'),
                                   number=100, delay=1):
    print('Sample data location: "' + video_loc + '"')
    for i in range(number):
        print('Progress frames: %d/%d' % (i, number))
        print('Estimated remaining time: %d sec' % ((number-i)*delay+(number-i)*0.1))
        image = get_frame_from_stream(camera)
        print('Creating cutout: ' + 'camera%d_frame%s.jpg' % (camera.id, strftime("%Y_%m_%d-%H_%M_%S", gmtime())))
        cv2.imwrite(os.path.join(video_loc, 'camera%d_frame_%s.jpg'
                                 % (camera.id, strftime("%Y_%m_%d-%H_%M_%S", gmtime()))), image)
        create_cutouts_from_image(camera, image)
        time.sleep(delay)
    print('Data sampling complete')


# noinspection PyArgumentList
def create_sample_data_from_nonstream(camera, video_loc=os.path.join(PROJECT_ROOT, 'media', 'tmp', 'new_data')):
    print('Sample data location: "' + video_loc + '"')
    cap = cv2.VideoCapture(camera.streamUrl)
    while not cap.isOpened():
        cap = cv2.VideoCapture(camera.streamUrl)
        time.sleep(1)
        print("Loading video: " + camera.streamUrl)

    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    fps = 20
    iterator = fps
    while True:
        flag, frame = cap.read()
        if fps == iterator:
            iterator = 1
            if flag:
                # The frame is ready and already captured
                print('Creating cutout: ' + 'camera%d_frame%s.jpg' % (camera.id, strftime("%Y_%m_%d-%H_%M_%S", gmtime())))
                cv2.imwrite(os.path.join(video_loc, 'camera%d_frame_%s.jpg'
                                         % (camera.id, strftime("%Y_%m_%d-%H_%M_%S", gmtime()))), frame)
                create_cutouts_from_image(camera, frame)
                time.sleep(1)
            else:
                # The next frame is not ready, so we try to read it again
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
                # It is better to wait for a while for the next frame to be ready
                time.sleep(1)
        else:
            iterator += 1
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            # If the number of captured frames is equal to the total number of frames,
            # we stop
            break
    cap.release()


def create_cutouts_from_image(camera, image):
    spots = ParkingSpot.objects.filter(camera=camera)
    print('Cutouts location: "' + os.path.join(PROJECT_ROOT, 'media', 'tmp', 'new_train_data') + '"')
    for spot in spots:
        if spot.rotation is None or spot.rotatedCordX is None or spot.rotatedCordY is None:
            save_parking_spot(spot, image)
        img = rotate_image(image, spot)
        img = cut_from_image(img, spot.leftUpperX, spot.leftUpperY, spot.rotatedCordX, spot.rotatedCordY)
        img = cv2.resize(img, dsize=(299, 299), interpolation=cv2.INTER_CUBIC)
        print('Creating cutout: camera%d_frame_%s_spot%d.jpg'
              % (camera.id, strftime("%Y_%m_%d-%H_%M_%S", gmtime()), spot.id))
        cv2.imwrite(
            os.path.join(PROJECT_ROOT, 'media', 'tmp', 'new_train_data', 'camera%d_frame_%s_spot%d.jpg'
                         % (camera.id, strftime("%Y_%m_%d-%H_%M_%S", gmtime()), spot.id)), img)


def run_recognition():
    cameras = Camera.objects.all()
    recon_threads = []
    graph = Graph.objects.latest('date')
    for camera in cameras:
        if camera.isStream:
            t = threading.Thread(target=run_camera_recognition, args=[camera, graph])
        else:
            t = threading.Thread(target=run_camera_recognition_nonstream, args=[camera, graph])
        t.start()
        recon_threads.append(t)
    return recon_threads


def cancel_recognition(recognition_threads, force=False):
    if not force:
        for thread in recognition_threads:
            if thread.isAlive():
                thread.do_run = False
                thread.join()
    else:
        for thread in recognition_threads:
            if thread.isAlive():
                thread.do_run = False
                thread.set()
    print('Thread canceled.')


def run_camera_recognition(camera, graph):
    print('Recognition started on camera %d - %s' % (camera.id, camera.name))
    t = threading.currentThread()
    spots = ParkingSpot.objects.filter(camera=camera.id)
    while getattr(t, "do_run", True):
        frame = get_frame_from_stream(camera)
        do_spots_iteration_on_frame(spots, frame, graph)
        time.sleep(5)


# noinspection PyArgumentList
def run_camera_recognition_nonstream(camera, graph):
    print('Recognition started on camera %d - %s' % (camera.id, camera.name))
    spots = ParkingSpot.objects.filter(camera=camera.id)
    cap = cv2.VideoCapture(camera.streamUrl)
    while not cap.isOpened():
        cap = cv2.VideoCapture(camera.streamUrl)
        time.sleep(1)
    fps = 24
    iterator = fps
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    while True:
        if iterator == fps:
            iterator = 1
            flag, frame = cap.read()
            if flag:
                do_spots_iteration_on_frame(spots, frame, graph)
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
        else:
            cap.grab()
            iterator += 1

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            break
    cap.release()


def do_spots_iteration_on_frame(spots, frame, graph):
    data = []
    for spot in spots:
        if spot.rotation is None or spot.rotatedCordX is None or spot.rotatedCordY is None:
            save_parking_spot(spot, frame)
        rotated_img = rotate_image(frame, spot)
        cropped_img = cut_from_image(rotated_img, spot.leftUpperX, spot.leftUpperY,
                                     spot.rotatedCordX, spot.rotatedCordY)
        img = cv2.resize(cropped_img, dsize=(299, 299), interpolation=cv2.INTER_CUBIC)
        filename = os.path.join(PROJECT_ROOT, 'media', 'tmp', 'classification_data', 'img%s_spot%d.jpg'
                                % (strftime("%Y_%m_%d-%H_%M_%S", gmtime()), spot.id))
        cv2.imwrite(filename, img)
        dataitem = {'spot': spot,
                    'img': filename}
        data.append(dataitem)
    do_recognition_on_images(data, graph)


def do_recognition_on_images(data, graph):
    classify(data, graph)

