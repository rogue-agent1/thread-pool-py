#!/usr/bin/env python3
"""Thread pool executor from scratch."""
import threading, queue, time, sys

class ThreadPool:
    def __init__(self, num_workers=4):
        self.tasks = queue.Queue(); self.results = {}; self.workers = []
        self.lock = threading.Lock(); self._task_id = 0; self._shutdown = False
        for _ in range(num_workers):
            t = threading.Thread(target=self._worker, daemon=True); t.start()
            self.workers.append(t)
    def _worker(self):
        while not self._shutdown:
            try:
                tid, fn, args, kwargs = self.tasks.get(timeout=0.1)
                try: result = fn(*args, **kwargs); error = None
                except Exception as e: result = None; error = e
                with self.lock: self.results[tid] = (result, error)
            except queue.Empty: continue
    def submit(self, fn, *args, **kwargs):
        with self.lock: self._task_id += 1; tid = self._task_id
        self.tasks.put((tid, fn, args, kwargs)); return tid
    def get_result(self, tid, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            with self.lock:
                if tid in self.results: return self.results.pop(tid)
            time.sleep(0.01)
        raise TimeoutError(f"Task {tid} timed out")
    def shutdown(self): self._shutdown = True

if __name__ == "__main__":
    pool = ThreadPool(4)
    def compute(n): time.sleep(0.05); return n * n
    tasks = [pool.submit(compute, i) for i in range(8)]
    for tid in tasks:
        result, error = pool.get_result(tid)
        print(f"Task {tid}: {result}")
    pool.shutdown()
