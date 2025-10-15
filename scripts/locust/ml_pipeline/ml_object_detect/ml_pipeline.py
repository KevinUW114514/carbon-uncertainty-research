import base64
import json
import logging
import os
import pickle
import random
import string
import sys
import time
import uuid
from pathlib import Path
import pickle

import numpy as np
import urllib3

import threading
import locust.stats
from locust import HttpUser, LoadTestShape, TaskSet, between, constant, tag, task, events
from locust.contrib.fasthttp import FastHttpUser
from locust.runners import MasterRunner

import statistics
import pandas as pd

# PROJECT_DIR = Path(__file__).resolve().parents[1]
# sys.path.append(str(PROJECT_DIR))

locust.stats.CSV_STATS_INTERVAL_SEC = 1  # second
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
random.seed(114514)
logging.basicConfig(level=logging.INFO)

nproc = 1
csv_file = f"ml_image_processing_results_{nproc}_cores.csv"
pickle_file = f"ml_image_processing_data_{nproc}_cores.pkl"
txt_file = "ml_image_processing_summary.log"

def create_summary():
    # Helper to summarize a list of numbers
    def summarize(name, data):
        return {
            "metric": name,
            "count": len(data),
            "avg": statistics.mean(data),
            "min": min(data),
            "max": max(data),
            "stdev": statistics.stdev(data) if len(data) > 1 else 0,
        }
    
    with open(pickle_file, "rb") as pf:
        existing_data = pickle.load(pf)
        main_duration = existing_data["main_duration_ms"]
        minio_get = existing_data["minio_get_ms"]
        minio_put = existing_data["minio_put_ms"]

    stats = [
        summarize("main_duration_ms", main_duration),
        summarize("minio_get_ms", minio_get),
        summarize("minio_put_ms", minio_put),
    ]

    # Display nicely    
    with open(txt_file, "a") as f:
        f.write(f"\nSummary for {1} vCPUs:\n")
        for s in stats:
            f.write(f"{s['metric']:>20}: avg={s['avg']:.2f}, min={s['min']}, max={s['max']}, stdev={s['stdev']:.2f}\n")
    

def process_results(results):
    # Helper to summarize a list of numbers

    df = pd.DataFrame(results, columns=["image_name", "size", "main_duration_ms", "minio_get_ms", "minio_put_ms"])
    # Unpack into separate lists
    main_durations = [r[2] for r in results]
    minio_gets = [r[3] for r in results]
    minio_puts = [r[4] for r in results]

    with lock:
        # === Write or append to CSV ===
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode="a", index=False, header=False)
        else:
            df.to_csv(csv_file, mode="w", index=False, header=True)

        data_to_add = {
            "main_duration_ms": main_durations,
            "minio_get_ms": minio_gets,
            "minio_put_ms": minio_puts,
        }

        if os.path.exists(pickle_file):
            # Append to existing pickle
            with open(pickle_file, "rb") as pf:
                existing_data = pickle.load(pf)

            # Extend existing lists
            for key, values in data_to_add.items():
                if key in existing_data:
                    existing_data[key].extend(values)
                else:
                    existing_data[key] = values

            with open(pickle_file, "wb") as pf:
                pickle.dump(existing_data, pf)
        else:
            # Create new pickle file
            with open(pickle_file, "wb") as pf:
                pickle.dump(data_to_add, pf)


ACTION_NAME = "ml_preprocessing_image"

path = "/home/cc/carbon/benchmarks/containerized/ml/image-processing/images"
files_with_sizes = [
    (f, os.path.getsize(os.path.join(path, f)))
    for f in os.listdir(path)
    if os.path.isfile(os.path.join(path, f))
][:50]

results = []
lock = threading.Lock()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    global results

    if not isinstance(environment.runner, MasterRunner):
        process_results(results)
        logging.info(f"Worker {environment.runner.client_id} finished.")
    else:
        create_summary()
        logging.info("Stopped test from Master node")


class ServerlessUser(FastHttpUser):
    host = "http://localhost:8124"

    def wait_time(self):
        return random.expovariate(1.4)  # mean 0.7s

    @tag(ACTION_NAME)
    @task(10)
    def ml_pipeline(self):
        global files_with_sizes, results

        image = random.choice(files_with_sizes)
        image_name = image[0]
        image_name = Path(image_name).stem + "_processed" + Path(image_name).suffix
        action_params = {"image_name": image_name}
        # url_params = {"blocking": "true", "result": "false"}
        response = self.client.post(
            url="/ping",
            # params=url_params,
            json=action_params,
            # auth=(USER_PASS[0], USER_PASS[1]),
            name=ACTION_NAME,
        )
        data = response.json()
        timestamps = data["timestamps"]
        main_end_ms, main_start_ms, minio_get_ms, minio_put_ms = (
            timestamps["main_end_ms"],
            timestamps["main_start_ms"],
            timestamps["minio_get_ms"],
            timestamps["minio_put_ms"]
        )
        results.append((image[0], image[1], main_end_ms - main_start_ms, minio_get_ms, minio_put_ms))




# class StagesShape(LoadTestShape):
#     # stages = [
#     #     {"duration": 30, "users": 500, "spawn_rate": 100},
#     #     {"duration": 60, "users": 600, "spawn_rate": 100},
#     #     {"duration": 90, "users": 700, "spawn_rate": 100},
#     #     {"duration": 120, "users": 800, "spawn_rate": 100},
#     #     {"duration": 150, "users": 900, "spawn_rate": 100},
#     #     {"duration": 180, "users": 1000, "spawn_rate": 100},
#     # ]
#     with open("/mnt/locust/trace.pickle", "rb") as fp:  # Unpickling
#         stages = pickle.load(fp)

#     def tick(self):
#         run_time = self.get_run_time()

#         self.stages = self.stages
#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 tick_data = (stage["users"], stage["spawn_rate"])
#                 return tick_data

#         return None
