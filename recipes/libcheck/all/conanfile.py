from conans import CMake, ConanFile, tools
import os


class LibCheckConan(ConanFile):
    name = "libcheck"
    description = "A unit testing framework for C"
    topics = "conan", "libcheck", "unit", "testing", "framework", "C"
    license = "https://github.com/libcheck/check"
    homepage = "https://github.com/libcheck/check"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_subunit": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_subunit": True,
    }

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_subunit:
            self.requires("subunit/1.4.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CHECK_ENABLE_TESTS"] = False
        self._cmake.definitions["ENABLE_MEMORY_LEAKING_TESTS"] = False
        self._cmake.definitions["CHECK_ENABLE_TIMEOUT_TESTS"] = False
        self._cmake.definitions["HAVE_SUBUNIT"] = self.options.with_subunit
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.LESSER", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "check"
        self.cpp_info.filenames["cmake_find_package_multi"] = "check"
        self.cpp_info.filenames["pkg_config"] = "check"

        self.cpp_info.names["cmake_find_package"] = "Check"
        self.cpp_info.names["cmake_find_package_multi"] = "Check"

        libsuffix = ""
        if self.options.shared:
            if self.settings.compiler == "Visual Studio":
                libsuffix = "Dynamic"

        self.cpp_info.components["liblibcheck"].libs = ["check" + libsuffix]
        if self.options.with_subunit:
            self.cpp_info.components["liblibcheck"].requires.append("subunit::libsubunit")
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["liblibcheck"].system_libs = ["m", "pthread", "rt"]

        self.cpp_info.components["liblibcheck"].names["cmake_find_package"] = "checkShared" if self.options.shared else "check"
        self.cpp_info.components["liblibcheck"].names["cmake_find_package_multi"] = "checkShared" if self.options.shared else "check"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
