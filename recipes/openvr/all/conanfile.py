import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

class OpenvrConan(ConanFile):
    name = "openvr"
    description = "API and runtime that allows access to VR hardware from applications have specific knowledge of the hardware they are targeting."
    topics = ("conan", "openvr", "vr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/openvr"
    license = "BSD-3-Clause"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "11")

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("OpenVR can't be compiled by {0} {1}".format(self.settings.compiler,
                                                                                         self.settings.compiler.version))

    def requirements(self):
        self.requires("jsoncpp/1.9.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Honor fPIC=False
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "-fPIC", "")
        # Unvendor jsoncpp (we rely on our CMake wrapper for jsoncpp injection)
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "jsoncpp.cpp", "")
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "src", "json"))

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
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="openvr_api*.dll", dst="bin", src="bin", keep_path=False)
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "openvr"
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.includedirs.append(os.path.join("include", "openvr"))

        if not self.options.shared:
            self.cpp_info.defines.append("OPENVR_BUILD_STATIC")
            libcxx = tools.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("Foundation")
