import threading, glob

from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from app.domain.entities.basic import *
from app.data.datasource.datasource import Datasource

class ImageDataSyncProvider():

    def __init__(self):
        self.event = threading.Event()
        
        # sync
        def handling():
            local_ds = Datasource()

            imagekit = ImageKit(
                private_key = 'private_7RAKTs0zAEM2oUg7byofL9j+wdE=',
                public_key  = 'public_DdAzc9DtVVj5Mnl6a9iy4AbklyU=',
                url_endpoint = 'https://ik.imagekit.io/4l58a99gt'
            )

            options = UploadFileRequestOptions(
                use_unique_file_name=False,
                overwrite_file=True
            )

            while True:
                if self.event.is_set():
                    jobs = local_ds.list_jobs()
                    i = 1

                    for job in jobs:
                        print(f"Job {i}/{len(jobs)}")
                        for file in glob.glob(f"cv-node-data/output/{job.id}/DEPTH/*.png"):
                            try:
                                upload = imagekit.upload_file(
                                        file = open(file, "rb"),
                                        file_name = file.split('/')[-1],
                                        options = options
                                    )
                                print(f"Created: {file.split('/')[-1]}")

                            except Exception as err:
                                print(f'{job.id} - Unexpected {err=}, {type(err)=}')

                        i+=1
                        break
                    self.event.clear()
                else:
                    self.event.wait()
             
        t = threading.Thread(target = handling)
        t.start()

    def start(self):
        self.event.set()
        print('sync on') 