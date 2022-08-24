import os
import shutil
import glob
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


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
        "build_aeron_driver": [True, False],
        "build_aeron_archive_api": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_aeron_driver": True,
        "build_aeron_archive_api": True
    }
    generators = "cmake"

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

    def build_requirements(self):
        self.build_requires("zulu-openjdk/11.0.8")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)

        compiler = str(self.settings.compiler)
        compiler_version = tools.scm.Version(self, self.settings.compiler.version)

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "5"
        }

        if compiler in minimal_version and compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires {} compiler {} or newer [is: {}]".format(self.name, compiler, minimal_version[compiler], compiler_version)
            )
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This platform (os=Macos arch=armv8) is not yet supported by this recipe")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["AERON_INSTALL_TARGETS"] = True
        self._cmake.definitions["BUILD_AERON_DRIVER"] = self.options.build_aeron_driver
        self._cmake.definitions["AERON_TESTS"] = False
        self._cmake.definitions["AERON_BUILD_SAMPLES"] = False
        self._cmake.definitions["BUILD_AERON_ARCHIVE_API"] = self.options.build_aeron_archive_api
        self._cmake.definitions["AERON_ENABLE_NONSTANDARD_OPTIMIZATIONS"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"), "/MTd", "")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"), "/MT", "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        with tools.files.chdir(self, self.package_folder):
            for dll in glob.glob(os.path.join("lib", "*.dll")):
                shutil.move(dll, "bin")

        archive_resources_dir = os.path.join(self._source_subfolder, "aeron-archive", "src", "main", "resources")
        self.copy("*", dst="res", src=archive_resources_dir)

        archive_include_dir = os.path.join(self._source_subfolder, "aeron-archive", "src", "main", "cpp", "client")
        self.copy("*.h", dst=os.path.join("include", "aeron-archive"), src=archive_include_dir)

        libs_folder = os.path.join(self.package_folder, "lib")
        if self.options.shared:
            tools.files.rm(self, libs_folder, "*.a")
            tools.files.rm(self, libs_folder, "*static.lib")
            tools.files.rm(self, libs_folder, "aeron_client.lib")
        else:
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.dll")
            tools.files.rm(self, libs_folder, "*.so")
            tools.files.rm(self, libs_folder, "*.dylib")
            tools.files.rm(self, libs_folder, "*shared.lib")
            tools.files.rm(self, libs_folder, "aeron.lib")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["wsock32", "ws2_32", "Iphlpapi"]
            self.cpp_info.defines.append("HAVE_WSAPOLL")
