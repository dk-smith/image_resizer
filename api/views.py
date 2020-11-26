from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from celery import current_app
from .tasks import resize
import json
import requests
from PIL import Image, ImageFile
import shutil
from django.conf import settings
import os
import threading 
from .models import *

ImageFile.LOAD_TRUNCATED_IMAGES = True

class ResizeThread(threading.Thread):
    def __init__(self, image_obj, url, size):
        threading.Thread.__init__(self)
        self.image_obj = image_obj
        self.url = url
        self.size = size

    def run(self):
        filename = self.url.split("/")[-1]
        r = requests.get(self.url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            image = Image.open(r.raw)
            new_image = image.resize((int(self.size['w']), int(self.size['h'])))
            filename = os.path.join(str(self.image_obj.id),filename)
            abs_path = os.path.join(settings.MEDIA_ROOT,filename)
            if not os.path.exists(os.path.dirname(abs_path)):
                os.makedirs(os.path.dirname(abs_path))
            new_image.save(abs_path+'.'+str(image.format), image.format)
            self.image_obj.image = filename
            self.image_obj.status = 1
        else:
            self.image_obj.status = 2
        self.image_obj.save()

def image(request):
    if request.method == 'GET':
        task_id = request.GET['id']
        image_obj = ImageModel.objects.get(id=task_id)
        data = {'status': image_obj.status, 'url': ''}
        if image_obj.status == 1:
            data['url'] = image_obj.image.url
        return JsonResponse(data, safe=True) 
    elif request.method == 'POST':
        body = json.loads(request.body)
        url = body['url']
        size = body['size']
        image_obj = ImageModel()
        image_obj.save()
        thread = ResizeThread(image_obj, url, size).run()
        data = {'id': image_obj.id}
        return JsonResponse(data, safe=True)
    return HttpResponse('response')

    

