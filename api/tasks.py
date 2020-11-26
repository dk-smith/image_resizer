from __future__ import absolute_import, unicode_literals

from celery import shared_task

import requests
from PIL import Image
import shutil
import os
from django.conf import settings

@shared_task
def add(x, y):
    return x + y

@shared_task
def resize(url, size):
    filename = url.split("/")[-1]
    r = requests.get(url, stream = True)
    if r.status_code == 200:
        r.raw.decode_content = True
        image = Image.open(r.raw)
        new_image = image.resize((size['w'], size['h']))
        new_image.save(os.path.join(settings.MEDIA_ROOT,filename))
        print("IMAGE RESIZED")
    else:
        print("ERROR")
