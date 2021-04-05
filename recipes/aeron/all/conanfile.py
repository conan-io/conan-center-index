import os
import shutil
import re
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class AeronConan(ConanFile):
    name = "aeron"
    description = "Efficient reliable UDP unicast, UDP multicast, and IPC message transport"
    topics = ("conan", "aeron", "udp", "messaging", "low-latency")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/real-logic/aeron/wiki"
    license = "Apache-2.0"
    exports_sources = "CMakeLists.txt",
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_aeron_driver": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_aeron_driver": False
    }
    generators = "cmake",

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("{} option shared=True is not supported on Windows", self.name)

        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if compiler == "Visual Studio" and self.settings.arch != "x86_64":
            # https://github.com/real-logic/aeron#c-build
            raise ConanInvalidConfiguration("{} currently only supports 64-bit builds on Windows".format(self.name))

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "5",
            "clang": "6",
            "apple-clang": "8"
        }

        if compiler in minimal_version and compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires {} compiler {} or newer [is: {}]".format(self.name, compiler, minimal_version[compiler], compiler_version)
            )

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("pthreads4w/3.0.0")

    def build_requirements(self):
        self.build_requires("zulu-openjdk/11.0.8")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake = CMake(self)
        cmake.definitions["AERON_INSTALL_TARGETS"] = True
        cmake.definitions["BUILD_AERON_DRIVER"] = self.options.build_aeron_driver
        cmake.definitions["AERON_TESTS"] = False
        cmake.definitions["AERON_BUILD_SAMPLES"] = False
        cmake.definitions["BUILD_AERON_ARCHIVE_API"] = True
        cmake.definitions["AERON_ENABLE_NONSTANDARD_OPTIMIZATIONS"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        # Files install straight to './include', but we want './include/aeron'
        old_include_folder = os.path.join(self.package_folder, "include")
        new_include_folder = os.path.join(self.package_folder, "include", self.name)
        tools.rmdir(new_include_folder)
        tools.mkdir(new_include_folder)

        files = os.listdir(old_include_folder)
        with tools.chdir(self.package_folder):
            for f in files:
                shutil.move(os.path.join(old_include_folder, f), new_include_folder)

        # additional resources
        archive_resources_dir = os.path.join(self._source_subfolder, "aeron-archive", "src", "main", "resources")
        self.copy("*", dst="res", src=archive_resources_dir)

        # archive client headers
        archive_include_dir = os.path.join(self._source_subfolder, "aeron-archive", "src", "main", "cpp", "client")
        self.copy("*.h", dst="include/aeron-archive", src=archive_include_dir)

        libs_folder = os.path.join(self.package_folder, "lib")
        if self.options.shared:
            tools.remove_files_by_mask(libs_folder, "libaeron.so")
            tools.remove_files_by_mask(libs_folder, "aeron.dll")
            tools.remove_files_by_mask(libs_folder, "libaeron.dylib")
            tools.remove_files_by_mask(libs_folder, "*.a")
            tools.remove_files_by_mask(libs_folder, "*.lib")
        else:
            tools.remove_files_by_mask(libs_folder, "libaeron_static.a")
            tools.remove_files_by_mask(libs_folder, "aeron.lib")
            tools.remove_files_by_mask(libs_folder, "aeron_static.lib")
            tools.remove_files_by_mask(libs_folder, "aeron_client_shared.lib")
            tools.remove_files_by_mask(libs_folder, "*.dll")
            tools.remove_files_by_mask(libs_folder, "*.so")
            tools.remove_files_by_mask(libs_folder, "*.dylib")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append("include/{}".format(self.name))

        # See: https://github.com/real-logic/aeron/blob/23f9ef8c6bd25955c3a64454f4e5d9c4a86c8d5a/CMakeLists.txt#L213
        self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")

        resources_folder = os.path.join(self.package_folder, "res")
        self.user_info.RESOURCES_DIR = resources_folder
        self.user_info.VERSION = self.version
