from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.33.0"

class QuillConan(ConanFile):
    name = "quill"
    description = "C++14 Asynchronous Low Latency Logging Library"
    topics = ("quill", "logging", "log")
    license = "MIT"
    homepage = "https://github.com/odygrd/quill/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        supported_archs = ["x86", "x86_64", "armv6", "armv7", "armv7hf", "armv8"]

        if not any(arch in str(self.settings.arch) for arch in supported_archs):
            raise ConanInvalidConfiguration("{} is not supported by {}".format(self.settings.arch, self.name))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("Quill requires C++14, which your compiler does not support.")
        else:
            self.output.warn("Quill requires C++14. Your compiler is unknown. Assuming it supports C++14.")

    def requirements(self):
        if tools.Version(self.version) >= "1.6.3":
            self.requires("fmt/8.1.1")
        elif tools.Version(self.version) >= "1.3.3":
            self.requires("fmt/7.1.3")
        else:
            self.requires("fmt/6.2.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

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
        if tools.Version(self.version) < "1.3.3" and tools.Version(self.deps_cpp_info["fmt"].version) > "6.2.1":
            raise ConanInvalidConfiguration("The project {}/{} requires fmt <= 6.2.1".format(self.name, self.version))

        # remove bundled fmt
        tools.rmdir(os.path.join(self._source_subfolder, "quill", "quill", "include", "quill", "bundled", "fmt"))
        tools.rmdir(os.path.join(self._source_subfolder, "quill", "quill", "src", "bundled", "fmt"))

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines = ["QUILL_FMT_EXTERNAL"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
