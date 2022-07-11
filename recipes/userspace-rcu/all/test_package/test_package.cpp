#include <benchmark/benchmark.h>

#include <atomic>
#include <iostream>
#include <mutex>
#include <thread>

#include "urcu_helper.hpp"

RCU_REGISTER_INIT

#define ITERATIONS 10000
#define THREADS 8

struct MyStatus {
  bool is_shutdown{false};
  bool is_paused{false};

  MyStatus() = default;
  MyStatus(const MyStatus& other) = default;
};

struct AtomicStatus {
  std::atomic<bool> is_shutdown{false};
  std::atomic<bool> is_paused{false};
};

#define NENTRIES_PER_THREAD 50

std::unique_ptr<AtomicStatus> glob_atomic_status;
test_package::urcu_scoped_ptr<MyStatus> glob_urcu_status;
std::unique_ptr<MyStatus> glob_raw_status;
std::mutex glob_mutex;

void setup() {
  glob_atomic_status = std::make_unique<AtomicStatus>();
  glob_raw_status = std::make_unique<MyStatus>();
}

void parallel_update() {
  auto t = std::thread([]() {
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      glob_atomic_status->is_shutdown.store(true);
      glob_atomic_status->is_paused.store(true);

      glob_raw_status->is_shutdown = true;
      glob_raw_status->is_paused = true;

      glob_urcu_status.update([](MyStatus* s) {
        s->is_shutdown = true;
        s->is_paused = true;
      });

      {
        std::lock_guard<std::mutex> l(glob_mutex);
        glob_raw_status->is_shutdown = true;
        glob_raw_status->is_paused = true;
      }
    }
    std::cout << "Updated all status" << std::endl;
  });
  t.detach();
}

void test_atomic_gets(benchmark::State& state) {
  auto t = std::thread([]() {
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      glob_atomic_status->is_shutdown.store(true);
      glob_atomic_status->is_paused.store(true);
    }
    std::cout << "Updated all status" << std::endl;
  });

  for (auto _ : state) {  // Loops upto iteration count
    bool ret;
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      benchmark::DoNotOptimize(ret = glob_atomic_status->is_shutdown.load());
      benchmark::DoNotOptimize(ret = glob_atomic_status->is_paused.load());
    }
  }
  t.join();
}

void test_urcu_gets(benchmark::State& state) {
  rcu_register_thread();
  auto t = std::thread([]() {
    rcu_register_thread();
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      glob_urcu_status.update([](MyStatus* s) {
        s->is_shutdown = true;
        s->is_paused = true;
      });
    }
    std::cout << "Updated all status" << std::endl;
    rcu_unregister_thread();
  });

  for (auto _ : state) {
    bool ret;
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      benchmark::DoNotOptimize(ret = glob_urcu_status.access()->is_shutdown);
      benchmark::DoNotOptimize(ret = glob_urcu_status.access()->is_paused);
    }
  }
  t.join();
  rcu_unregister_thread();
}

void test_raw_gets(benchmark::State& state) {
  parallel_update();
  for (auto _ : state) {
    bool ret;
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      benchmark::DoNotOptimize(ret = glob_raw_status->is_shutdown);
      benchmark::DoNotOptimize(ret = glob_raw_status->is_paused);
    }
  }
}

void test_mutex_gets(benchmark::State& state) {
  parallel_update();
  for (auto _ : state) {
    bool ret;
    for (auto i = 0U; i < NENTRIES_PER_THREAD; i++) {
      std::lock_guard<std::mutex> l(glob_mutex);
      benchmark::DoNotOptimize(ret = glob_raw_status->is_shutdown);
      benchmark::DoNotOptimize(ret = glob_raw_status->is_paused);
    }
  }
}

BENCHMARK(test_atomic_gets)->Iterations(ITERATIONS)->Threads(THREADS);
BENCHMARK(test_urcu_gets)->Iterations(ITERATIONS)->Threads(THREADS);
BENCHMARK(test_raw_gets)->Iterations(ITERATIONS)->Threads(THREADS);
BENCHMARK(test_mutex_gets)->Iterations(ITERATIONS)->Threads(THREADS);

int main(int argc, char** argv) {
  setup();
  ::benchmark::Initialize(&argc, argv);
  ::benchmark::RunSpecifiedBenchmarks();
}
