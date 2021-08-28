#include "mcs_lock.hpp"

#include <cassert>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <thread>
#include <vector>

template <typename Lock> void counter(Lock &l, uint64_t &cnt, uint64_t num) {
  for (uint64_t i = 0; i < num; ++i) {
    l.lock();
    cnt++;
    l.unlock();
  }
}

template <typename Lock>
void test_lock(size_t n_threads, uint64_t cnt_per_thread) {
  alignas(64) Lock m;
  alignas(64) uint64_t cnt = 0;
  std::vector<std::thread> threads;
  threads.reserve(n_threads);
  for (int i = 0; i < n_threads; i++) {
    threads.emplace_back(counter<Lock>, std::ref(m), std::ref(cnt),
                         cnt_per_thread);
  }
  for (int i = 0; i < n_threads; i++) {
    threads[i].join();
  }
  assert(cnt == n_threads * cnt_per_thread);
}

int main(int argc, const char *argv[]) {
  if (argc != 3) {
    printf("num_threads counts_per_thread");
    exit(1);
  }

  size_t n = static_cast<size_t>(std::stoi(argv[1], nullptr, 10));
  uint64_t cnt_per_thread =
      static_cast<size_t>(std::stoi(argv[2], nullptr, 10));
  printf("Counting %lu x %lu with %lu threads\n", n, cnt_per_thread, n);

  auto t1 = std::chrono::high_resolution_clock::now();
  test_lock<std::mutex>(n, cnt_per_thread);
  auto t2 = std::chrono::high_resolution_clock::now();
  test_lock<MCSLock>(n, cnt_per_thread);
  auto t3 = std::chrono::high_resolution_clock::now();

  printf("Time taken (milliseconds):\n");
  printf(
      "    %-11s : %lu\n", "std::mutex",
      std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count());
  printf(
      "    %-11s : %lu\n", "MCSLock",
      std::chrono::duration_cast<std::chrono::milliseconds>(t3 - t2).count());
}
