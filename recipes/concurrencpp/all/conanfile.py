from conan.tools.microsoft import is_msvc
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class ConcurrencppConan(ConanFile):
    name = "concurrencpp"
    description = "Modern concurrency for C++. Tasks, executors, timers and C++20 coroutines to rule them all."
    homepage = "https://github.com/David-Haim/concurrencpp"
    topics = ("scheduler", "coroutines", "concurrency", "tasks", "executors", "timers", "await", "multithreading")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {"Visual Studio": "16", "msvc": "192", "clang": "11"}

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "20")
        if self.options.shared and is_msvc(self):
            # see https://github.com/David-Haim/concurrencpp/issues/75
            raise ConanInvalidConfiguration("concurrencpp does not support shared builds with Visual Studio")
        if self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("gcc is not supported by concurrencpp")

        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False
        )
        if not minimum_version:
            self.output.warn(
                "concurrencpp requires C++20. Your compiler is unknown. Assuming it supports C++20."
            )
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "concurrencpp requires clang >= 11 or Visual Studio >= 16.8.2 as a compiler!"
            )
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("libc++ required")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):        
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "concurrencpp")
        self.cpp_info.set_property("cmake_target_name", "concurrencpp::concurrencpp")
        self.cpp_info.libs = ["concurrencpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread", "rt"]
