import time
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from zeus.monitor import ZeusMonitor
from zeus.device.cpu import get_current_cpu_index

def hu(num):
    bei = 0
    nao = 0
    xi = 0
    for i in range(num):
        with open("hu.txt", "a+") as f:
            if i & 111:
                bei += i
                f.write(str(bei) + "\n")
            elif i | 11:
                xi += i
                f.write(str(xi) + "\n")
            else:
                nao += 1
                f.write(str(nao) + "\n")

if __name__ == "__main__":
    for i in range(2):
        os.remove("hu.txt") if os.path.exists("hu.txt") else None
        # monitor = ZeusMonitor(cpu_indices=[get_current_cpu_index("current")])
        monitor = ZeusMonitor()
        monitor.begin_window("hu")

        start_proc = time.process_time()
        start_os = os.times()
        start_clock = time.time()
        n = 24
        with ProcessPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(hu, 100000) for _ in range(n)]
            for future in futures:
                result = future.result()
                # print(result)

        # with ThreadPoolExecutor(max_workers=4) as executor:
        #     futures = [executor.submit(hu, 1000) for _ in range(4)]
        #     for future in futures:
        #         result = future.result()
        #         print(result)
        hu(10000)
                
        end_os = os.times()
        end_clock = time.time()
        end_proc = time.process_time()

        print("Wall clock time:", end_clock - start_clock)
        print("Process time:", end_proc - start_proc)
        print(f"aggregate time: { (end_os.user - start_os.user) + (end_os.system - start_os.system) }")
        print("User time:", end_os.user - start_os.user)
        print("System time:", end_os.system - start_os.system)
        print("Children user time:", end_os.children_user - start_os.children_user)
        print("Children system time:", end_os.children_system - start_os.children_system)
        print("Total Time:", end_os.elapsed - start_os.elapsed)

        result = monitor.end_window("hu")
        print(f"cpu energy: {result.cpu_energy}")
        print(f"dram energy: {result.dram_energy}")
        print("=" * 80)