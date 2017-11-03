from django.shortcuts import render, get_list_or_404, get_object_or_404
from .models import Camera, ParkingSpot
# noinspection PyPackageRequirements
from .utils import image_utils
# noinspection PyPackageRequirements
from PIL import Image


def index(request):
    if request.method == 'POST':
        url = request.POST.get('streamUrl', None)
        is_stream = request.POST.get('isStream', False)
        name = request.POST.get('name', None)
        is_mjpeg = request.POST.get('ismjpg', False)
        if url is not None and name is not None:
            c = Camera(name=name, streamUrl=url, isStream=is_stream, isMjpeg=is_mjpeg)
            c.save()
            save_status = c.pk is not None
            if c.pk is not None:
                save_msg = 'Camera was successfully saved.'
            else:
                save_msg = 'Error: While saving camera an error occurred.'
            cameras = get_list_or_404(Camera)
            context = {
                'cameras': cameras,
                'save_msg': save_msg,
                'save_status': save_status
            }
        else:
            cameras = get_list_or_404(Camera)
            context = {
                'cameras': cameras,
                'save_msg': 'Some values are not filled!',
                'save_status': False
            }
    else:
        cameras = get_list_or_404(Camera)
        context = {
            'cameras': cameras
        }
    return render(request, 'recognizer/index.html', context)


def camera_detail(request, camera_id):
    camera = get_object_or_404(Camera, pk=camera_id)
    img = image_utils.get_frame_from_stream(camera)
    img = Image.fromarray(img, 'RGB')
    img.save('static/imgs/tmp%d.jpg' % camera.id)
    if request.method == 'POST':
        data = request.POST
        lux = data['ulx']
        luy = data['uly']
        rux = data['urx']
        ruy = data['ury']
        rlx = data['lrx']
        rly = data['lry']
        llx = data['llx']
        lly = data['lly']
        ps = ParkingSpot(camera=camera_id, leftUpperX=lux, leftUpperY=luy, rightUpperX=rux, rightUpperY=ruy,
                         rightLowerX=rlx, rightLowerY=rly, leftLowerX=llx, leftLowerY=lly)
        ps.save()
        save_status = ps.pk is not None
        if ps.pk is not None:
            save_msg = 'Parking Spot successfully added!'
        else:
            save_msg = 'Error while saving Parking Spot!'
        parking_spots = get_list_or_404(ParkingSpot, camera=camera_id)
        context = {
            'camera': camera,
            'spots': parking_spots,
            'save_msg': save_msg,
            'save_status': save_status,
            'img': img
        }
    else:
        parking_spots = get_list_or_404(ParkingSpot, camera=camera_id)
        context = {
            'camera': camera,
            'spots': parking_spots,
            'img': img
        }
    return render(request, 'recognizer/camera_detail.html', context)


def remove_camera(request, camera_id):
    ParkingSpot.objects.filter(camera=camera_id).delete()
    Camera.objects.filter(pk=camera_id).delete()
    request.methods = request.GET
    return index(request)


def remove_parking_spot(request, spot_id):
    s = ParkingSpot.objects.filter(pk=spot_id)
    camera_id = s.pk
    s.delete()
    request.method = request.GET
    return camera_detail(request, camera_id)


def run(request):
    if request.method == 'POST':
        threads = request.POST['threads']
        if threads is None:
            threads = image_utils.run_recognition()
            msg = 'Threads are running'
            status = True
        else:
            image_utils.cancel_recognition(threads, False)
            threads = None
            status = False
            msg = 'Threads are stopped'
        context = {
            'run_status': status,
            'run_msg': msg,
            'running': threads is not None
        }
    else:
        context = {
            'running': None
        }
    return render(request, 'recognizer/run.html', context)
