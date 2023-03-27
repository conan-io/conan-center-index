from conan import ConanFile
from conan.tools.build import build_jobs, can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        libverto_options = self.dependencies["libverto"].options
        tc.variables["LIBVERTO_WITH_GLIB"] = bool(libverto_options.with_glib)
        tc.variables["LIBVERTO_WITH_LIBEV"] = bool(libverto_options.with_libev)
        tc.variables["LIBVERTO_WITH_LIBEVENT"] = bool(libverto_options.with_libevent)
        tc.variables["LIBVERTO_WITH_TEVENT"] = bool(libverto_options.with_tevent)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with chdir(self, self.build_folder):
                self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {build_jobs(self)}", env="conanrun")
