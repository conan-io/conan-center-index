from conan import ConanFile, tools
from conans import CMake
from conan.tools.microsoft import is_msvc
import os
import functools

required_conan_version = ">=1.33.0"

class ZyreConan(ConanFile):
    name = "zyre"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/zyre"
    description = "Local Area Clustering for Peer-to-Peer Applications."
    topics = ("zyre", "czmq", "zmq", "zeromq",
              "message-queue", "asynchronous")
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake", "cmake_find_package"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "drafts": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "drafts": False,
    }

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

    def requirements(self):
        self.requires("czmq/4.2.0")
        self.requires("zeromq/4.3.4")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libsystemd/249.7")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DRAFTS"] = self.options.drafts
        if tools.Version(self.version) >= "2.0.1":
            cmake.definitions["ZYRE_BUILD_SHARED"] = self.options.shared
            cmake.definitions["ZYRE_BUILD_STATIC"] = not self.options.shared
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder,
                  dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig",))
        tools.rmdir(os.path.join(self.package_folder, "share",))
        tools.rmdir(os.path.join(self.package_folder, "cmake",))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libzyre"
        
        libname = "libzyre" if tools.Version(self.version) >= "2.0.1" and is_msvc(self) and not self.options.shared else "zyre"
        self.cpp_info.libs = [libname]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "rt", "m"]
        if not self.options.shared:
            self.cpp_info.defines = ["ZYRE_STATIC"]
