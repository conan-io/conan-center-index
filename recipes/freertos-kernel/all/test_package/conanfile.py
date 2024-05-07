import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, options={
            "heap": "3",
            "max_priorities": "7",
            "use_counting_semaphores": True,
            "use_mutexes": True,
            "use_queue_sets": True,
            "use_recursive_mutexes": True,
            "use_timers": True,
            "tick_rate_hz": "( 1000 )",
            "timer_queue_length": 20,
            "timer_task_priority": "( configMAX_PRIORITIES - 1 )",
            "timer_task_stack_depth": "( configMINIMAL_STACK_SIZE * 2 )",
            "use_task_notifications": True,
            })

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
