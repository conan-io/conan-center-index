import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def configure(self):
        self.options[self.tested_reference_str].heap = "3"
        self.options[self.tested_reference_str].tick_rate_hz = "( 1000 )"
        self.options[self.tested_reference_str].minimal_stack_size = "( unsigned short ) PTHREAD_STACK_MIN )"
        self.options[self.tested_reference_str].minimal_heap_size = "( ( size_t ) ( 65 * 1024 ) )"
        self.options[self.tested_reference_str].use_mutexes = True
        self.options[self.tested_reference_str].use_recursive_mutexes = True
        self.options[self.tested_reference_str].use_counting_semaphores = True
        self.options[self.tested_reference_str].use_queue_sets = True
        self.options[self.tested_reference_str].use_timers = True
        self.options[self.tested_reference_str].timer_task_priority = "( configMAX_PRIORITIES - 1 )"
        self.options[self.tested_reference_str].timer_queue_length = 20
        self.options[self.tested_reference_str].timer_task_stack_depth = "( configMINIMAL_STACK_SIZE * 2 )"
        self.options[self.tested_reference_str].max_priorities = "( 7 )"
        self.options[self.tested_reference_str].use_task_notifications = True

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
