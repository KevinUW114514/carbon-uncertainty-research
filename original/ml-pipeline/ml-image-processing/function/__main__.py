import io
import pickle
from datetime import datetime, timezone
from multiprocessing import Pool
from pathlib import Path

import numpy as np
# from config import ACCESS_KEY, BUCKET, ENDPOINT, SECRET_KEY
from minio import Minio
from PIL import Image, ImageFilter

import sys
from pathlib import Path

sys.path.append("/home/cc/carbon/aquatope/benchmarks/common")

from utils import get_timestamp_ms, minio_get_image, minio_put_image

minio_client = None

def main(args=dict()):
    global minio_client

    # -----------------------------------------------------------------------
    # Parse params
    # -----------------------------------------------------------------------
    timestamps = {
        "main_start_ms": 0,
        "main_end_ms": 0,
        "minio_get_ms": 0,
        "minio_put_ms": 0,
    }
    timestamps["main_start_ms"] = get_timestamp_ms()
    endpoint = "localhost:9000"
    access_key = "ROOTNAME"
    secret_key = "CHANGEME123"
    bucket_name = "images"
    if minio_client is None:
        minio_client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )
    image_name = "346d09130465eeb68f1b1d3b243357e2.jpeg"

    # -----------------------------------------------------------------------
    # Action execution
    # -----------------------------------------------------------------------
    image = minio_get_image(
        minio_client=minio_client,
        bucket_name=bucket_name,
        image_name=image_name,
        timestamps=timestamps,
    )

    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image = image.transpose(Image.ROTATE_90)
    image = image.transpose(Image.ROTATE_180)
    image = image.transpose(Image.ROTATE_270)
    image = image.filter(ImageFilter.BLUR)
    image = image.filter(ImageFilter.CONTOUR)
    image = image.filter(ImageFilter.SHARPEN)
    image = image.convert("L")

    new_image_name = Path(image_name).stem + "_processed" + Path(image_name).suffix
    minio_put_image(
        minio_client=minio_client,
        bucket_name=bucket_name,
        image_name=new_image_name,
        image=image,
        timestamps=timestamps,
    )

    # -----------------------------------------------------------------------
    # Return results
    # -----------------------------------------------------------------------
    timestamps["main_end_ms"] = get_timestamp_ms()
    args["timestamps"] = timestamps
    return args

result = main()
print(result)