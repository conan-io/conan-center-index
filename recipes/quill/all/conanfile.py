from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
import os

class QuillConan(ConanFile):
    name = "quill"
    description = "C++14 Asynchronous Low Latency Logging Library"
    homepage = "https://github.com/odygrd/quill/"
    topics = ("conan", "quill", "logging", "log")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"

    options = {"fPIC": [True, False],
               "with_bounded_queue": [True, False],
               "with_no_exceptions": [True, False]}

    default_options = {"fPIC": True,
                       "with_bounded_queue": False,
                       "with_no_exceptions": False}

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
        supported_archs = ["x86", "x86_64", "armv6", "armv7", "armv7hf", "armv8"]

        if not any(arch in str(self.settings.arch) for arch in supported_archs):
            raise ConanInvalidConfiguration("{} is not supported by {}".format(self.settings.arch, self.name))

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "14")

        minimum_version = {
            "clang": "5",
            "gcc": "5",
            "Visual Studio": "15.0",
        }.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn(
                "Unknown compiler {} {}. Assuming compiler supports C++14".format(self.settings.compiler,
                                                                                  self.settings.compiler.version))

        else:
            version = Version(self.settings.compiler.version.value)
            if version < minimum_version:
                raise ConanInvalidConfiguration(
                    "The compiler {} {} does not support C++14".format(self.settings.compiler,
                                                                       self.settings.compiler.version))

    def requirements(self):
        self.requires("fmt/6.1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["QUILL_FMT_EXTERNAL"] = True
        self._cmake.definitions["QUILL_ENABLE_INSTALL"] = True
        self._cmake.definitions["QUILL_USE_BOUNDED_QUEUE"] = self.options.with_bounded_queue
        self._cmake.definitions["QUILL_NO_EXCEPTIONS"] = self.options.with_no_exceptions
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
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

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
