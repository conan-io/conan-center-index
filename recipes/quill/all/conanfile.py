from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.33.0"

class QuillConan(ConanFile):
    name = "quill"
    description = "Asynchronous Low Latency C++ Logging Library"
    topics = ("quill", "logging", "log", "async")
    license = "MIT"
    homepage = "https://github.com/odygrd/quill/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_bounded_queue": [True, False],
        "with_no_exceptions": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_bounded_queue": False,
        "with_no_exceptions": False,
    }
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_versions(self):
        return {
            "14":
                {
                    "gcc": "5",
                    "Visual Studio": "15",
                    "clang": "5",
                    "apple-clang": "10",
                },
            "17":
                {
                    "gcc": "8",
                    "Visual Studio": "16",
                    "clang": "7",
                    "apple-clang": "12",
                },
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        supported_archs = ["x86", "x86_64", "armv6", "armv7", "armv7hf", "armv8"]

        if not any(arch in str(self.settings.arch) for arch in supported_archs):
            raise ConanInvalidConfiguration("{} is not supported by {}".format(self.settings.arch, self.name))

        cxx_std = "17" if tools.Version(self.version) >= "2.0.0" else "14"

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, cxx_std)

        compilers_minimum_version = self._compilers_minimum_versions[cxx_std]
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++{}, which your compiler does not support.".format(self.name, cxx_std))
        else:
            self.output.warn("{} requires C++{}. Your compiler is unknown. Assuming it supports C++{}.".format(self.name, cxx_std, cxx_std))

        if tools.Version(self.version) >= "2.0.0" and \
            self.settings.compiler== "clang" and tools.Version(self.settings.compiler.version).major == "11" and \
            self.settings.compiler.libcxx == "libstdc++":
            raise ConanInvalidConfiguration("{}/{} requires C++ filesystem library, which your compiler doesn't support.".format(self.name, self.version))

    def requirements(self):
        if tools.Version(self.version) >= "1.6.3":
            self.requires("fmt/9.0.0")
        else:
            self.requires("fmt/7.1.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["QUILL_FMT_EXTERNAL"] = True
        cmake.definitions["QUILL_ENABLE_INSTALL"] = True
        cmake.definitions["QUILL_USE_BOUNDED_QUEUE"] = self.options.with_bounded_queue
        cmake.definitions["QUILL_NO_EXCEPTIONS"] = self.options.with_no_exceptions
        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        if tools.Version(self.version) >= "2.0.0":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                """set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_LIST_DIR}/quill/cmake" CACHE STRING "Modules for CMake" FORCE)""",
                """set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH};${CMAKE_CURRENT_LIST_DIR}/quill/cmake")"""
            )

        # remove bundled fmt
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "quill", "quill", "include", "quill", "bundled", "fmt"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "quill", "quill", "src", "bundled", "fmt"))

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.defines = ["QUILL_FMT_EXTERNAL"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if tools.Version(self.version) >= "2.0.0" and \
            self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")
