from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class OpenALConan(ConanFile):
    name = "openal"
    description = "OpenAL Soft is a software implementation of the OpenAL 3D audio API."
    topics = ("openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openal-soft.org/"
    license = "LGPL-2.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

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

    @property
    def _openal_cxx_backend(self):
        return tools.scm.Version(self, self.version) >= "1.20"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        # OpenAL's API is pure C, thus the c++ standard does not matter
        # Because the backend is C++, the C++ STL matters
        del self.settings.compiler.cppstd
        if not self._openal_cxx_backend:
            del self.settings.compiler.libcxx

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.2.5.1")

    @property
    def _supports_cxx14(self):
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx in ("libstdc++", "libstdc++11"):
            if tools.scm.Version(self, self.settings.compiler.version) < "9":
                return False, "openal on clang {} cannot be built with stdlibc++(11) c++ runtime".format(self.settings.compiler.version)
        min_version = {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
        }.get(str(self.settings.compiler))
        if min_version and tools.scm.Version(self, self.settings.compiler.version) < min_version:
            return False, "This compiler version does not support c++14"
        return True, None

    @property
    def _supports_cxx11(self):
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx in ("libstdc++", "libstdc++11"):
            if tools.scm.Version(self, self.settings.compiler.version) < "9":
                return False, "openal on clang {} cannot be built with stdlibc++(11) c++ runtime".format(self.settings.compiler.version)
        min_version = {
            "Visual Studio": "13",
            "gcc": "5",
            "clang": "5",
        }.get(str(self.settings.compiler))
        if min_version and tools.scm.Version(self, self.settings.compiler.version) < min_version:
            return False, "This compiler version does not support c++11"
        return True, None

    def validate(self):
        if tools.scm.Version(self, self.version) >= "1.21":
            ok, msg = self._supports_cxx14
            if not ok:
                raise ConanInvalidConfiguration(msg)
            if msg:
                self.output.warn(msg)
        elif tools.scm.Version(self, self.version) >= "1.20":
            ok, msg = self._supports_cxx11
            if not ok:
                raise ConanInvalidConfiguration(msg)
            if msg:
                self.output.warn(msg)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

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
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            if(DEFINED OpenAL_FOUND)
                set(OPENAL_FOUND ${OpenAL_FOUND})
            endif()
            if(DEFINED OpenAL_INCLUDE_DIR)
                set(OPENAL_INCLUDE_DIR ${OpenAL_INCLUDE_DIR})
            endif()
            if(DEFINED OpenAL_LIBRARIES)
                set(OPENAL_LIBRARY ${OpenAL_LIBRARIES})
            endif()
            if(DEFINED OpenAL_VERSION)
                set(OPENAL_VERSION_STRING ${OpenAL_VERSION})
            endif()
        """)
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenAL")
        self.cpp_info.set_property("cmake_target_name", "OpenAL::OpenAL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "openal")

        self.cpp_info.names["cmake_find_package"] = "OpenAL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenAL"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]

        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.includedirs.append(os.path.join("include", "AL"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
        elif tools.apple.is_apple_os(self, self.settings.os):
            self.cpp_info.frameworks.extend(["AudioToolbox", "CoreAudio", "CoreFoundation"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ole32", "shell32", "User32"])
        if self._openal_cxx_backend:
            libcxx = tools.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
        if not self.options.shared:
            self.cpp_info.defines.append("AL_LIBTYPE_STATIC")
