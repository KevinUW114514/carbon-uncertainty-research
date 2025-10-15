import statistics
import requests
import numpy as np
import os
import pandas as pd
import argparse
import time

args = argparse.ArgumentParser()
args.add_argument("-n", "--nume_of_vcpus", type=int, required=True)
args = args.parse_args()
nproc = args.nume_of_vcpus

path = "/home/cc/carbon/benchmarks/containerized/ml/image-processing/images"
BASE_URL = "http://localhost:8123"

def test_ping_endpoint(args):
    response = requests.post(f"{BASE_URL}/ping", json={"image_name": args[0]})
    assert response.status_code == 200
    data = response.json()
    timestamps = data["timestamps"]
    main_end_ms, main_start_ms, minio_get_ms, minio_put_ms = (
        timestamps["main_end_ms"],
        timestamps["main_start_ms"],
        timestamps["minio_get_ms"],
        timestamps["minio_put_ms"]
    )
    return args[0], args[1], (main_end_ms - main_start_ms), minio_get_ms, minio_put_ms

# Compute summary stats
def process_results(results, nproc):
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
    
    df = pd.DataFrame(results, columns=["image_name", "size", "main_duration_ms", "minio_get_ms", "minio_put_ms"])
    df.to_csv(f"ml_image_processing_results_{nproc}_cores.csv", index=False)

    # Unpack into separate lists
    main_durations = [r[2] for r in results]
    minio_gets = [r[3] for r in results]
    minio_puts = [r[4] for r in results]

    stats = [
        summarize("main_duration_ms", main_durations),
        summarize("minio_get_ms", minio_gets),
        summarize("minio_put_ms", minio_puts),
    ]

    # Display nicely    
    with open("ml_image_processing_summary.txt", "a") as f:
        f.write(f"\nSummary for {nproc} vCPUs:\n")
        for s in stats:
            f.write(f"{s['metric']:>20}: avg={s['avg']:.2f}, min={s['min']}, max={s['max']}, stdev={s['stdev']:.2f}\n")


if __name__ == "__main__":
    results = []

    os.system(f"docker run -d -p 8123:8123 --name ml_image_processing --cpus={nproc} --memory=1g --network local_net ml_image_processing")
    time.sleep(2)

    files_with_sizes = [
        (f, os.path.getsize(os.path.join(path, f)))
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]

    for f in files_with_sizes:
        results.append((test_ping_endpoint(f)))

    # process_results(results)

    os.system("docker stop ml_image_processing")
    os.system("docker container rm ml_image_processing")