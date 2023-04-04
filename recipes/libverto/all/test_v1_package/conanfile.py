from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LIBVERTO_WITH_GLIB"] = bool(self.options["libverto"].with_glib)
        cmake.definitions["LIBVERTO_WITH_LIBEV"] = bool(self.options["libverto"].with_libev)
        cmake.definitions["LIBVERTO_WITH_LIBEVENT"] = bool(self.options["libverto"].with_libevent)
        cmake.definitions["LIBVERTO_WITH_TEVENT"] = bool(self.options["libverto"].with_tevent)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
