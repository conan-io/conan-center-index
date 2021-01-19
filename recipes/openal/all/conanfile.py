import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class OpenALConan(ConanFile):
    name = "openal"
    description = "OpenAL Soft is a software implementation of the OpenAL 3D audio API."
    topics = ("conan", "openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openal.org"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
    @property
    def _supports_cxx14(self):
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx in ("libstdc++", "libstdc++11"):
            if tools.Version(self.settings.compiler.version) < "9":
                return False, "openal on clang {} cannot be built with stdlibc++(11) c++ runtime".format(self.settings.compiler.version)
        min_version = {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
        }.get(str(self.settings.compiler))
        if min_version:
            if tools.Version(self.settings.compiler.version) < min_version:
                return False, "This compiler version does not support c++14"
            else:
                return True, "Unknown compiler. Assuming your compiler supports c++14"
        return True, None

    @property
    def _supports_cxx11(self):
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx in ("libstdc++", "libstdc++11"):
            if tools.Version(self.settings.compiler.version) < "9":
                return False, "openal on clang {} cannot be built with stdlibc++(11) c++ runtime".format(self.settings.compiler.version)
        min_version = {
            "Visual Studio": "13",
            "gcc": "5",
            "clang": "5",
        }.get(str(self.settings.compiler))
        if min_version:
            if tools.Version(self.settings.compiler.version) < min_version:
                return False, "This compiler version does not support c++11"
            else:
                return True, "Unknown compiler. Assuming your compiler supports c++11"
        return True, None

    @property
    def _openal_cxx_backend(self):
        return tools.Version(self.version) >= "1.20"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        # OpenAL's API is pure C, thus the c++ standard does not matter
        # Because the backend is C++, the C++ STL matters
        del self.settings.compiler.cppstd
        if not self._openal_cxx_backend:
            del self.settings.compiler.libcxx

        if tools.Version(self.version) >= "1.21":
            ok, msg = self._supports_cxx14
            if not ok:
                raise ConanInvalidConfiguration(msg)
            if msg:
                self.output.warn(msg)
        elif tools.Version(self.version) >= "1.20":
            ok, msg = self._supports_cxx11
            if not ok:
                raise ConanInvalidConfiguration(msg)
            if msg:
                self.output.warn(msg)

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.2.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "openal-soft-openal-soft-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBTYPE"] = "SHARED" if self.options.shared else "STATIC"
        self._cmake.definitions["ALSOFT_UTILS"] = False
        self._cmake.definitions["ALSOFT_EXAMPLES"] = False
        self._cmake.definitions["ALSOFT_TESTS"] = False
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_SoundIO"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenAL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenAL"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "AL"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["AudioToolbox", "CoreAudio", "CoreFoundation"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ole32", "shell32", "User32"])
        if self._openal_cxx_backend:
            libcxx = tools.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
        if not self.options.shared:
            self.cpp_info.defines.append("AL_LIBTYPE_STATIC")
