import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

class OpenvrConan(ConanFile):
    name = "openvr"
    description = "API and runtime that allows access to VR hardware from applications have specific knowledge of the hardware they are targeting."
    topics = ("conan", "openvr", "vr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/openvr"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("OpenVR can't be compiled by {0} {1}".format(self.settings.compiler,
                                                                                         self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_UNIVERSAL"] = False
        self._cmake.definitions["USE_LIBCXX"] = False
        self._cmake.configure()

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="openvr_api*.dll", dst="bin", src="bin", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if not self.options.shared:
            self.cpp_info.defines.append('OPENVR_BUILD_STATIC')

        if self.settings.os != "Windows":
            self.cpp_info.libs.append("dl")

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Foundation")
