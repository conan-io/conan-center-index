from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rmdir, save
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os
import textwrap

required_conan_version = ">=1.51.3"


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

    @property
    def _openal_cxx_backend(self):
        return Version(self.version) >= "1.20"

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.21" else "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "13" if Version(self.version) < "1.21" else "15",
            "msvc": "180" if Version(self.version) < "1.21" else "191",
            "gcc": "5",
            "clang": "5",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        # OpenAL's API is pure C, thus the c++ standard does not matter
        # Because the backend is C++, the C++ STL matters
        del self.settings.compiler.cppstd
        if not self._openal_cxx_backend:
            del self.settings.compiler.libcxx

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.2.7.2")

    def validate(self):
        if self._openal_cxx_backend:
            if self.info.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, self._min_cppstd)

            compiler = self.info.settings.compiler

            minimum_version = self._minimum_compilers_version.get(str(compiler), False)
            if minimum_version and Version(compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
                )

            if compiler == "clang" and Version(compiler.version) < "9" and \
               compiler.get_safe("libcxx") in ("libstdc++", "libstdc++11"):
                raise ConanInvalidConfiguration(
                    f"{self.ref} cannot be built with {compiler} {compiler.version} and stdlibc++(11) c++ runtime",
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBTYPE"] = "SHARED" if self.options.shared else "STATIC"
        tc.variables["ALSOFT_UTILS"] = False
        tc.variables["ALSOFT_EXAMPLES"] = False
        tc.variables["ALSOFT_TESTS"] = False
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_SoundIO"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            set(OPENAL_FOUND TRUE)
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
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenAL")
        self.cpp_info.set_property("cmake_target_name", "OpenAL::OpenAL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "openal")

        self.cpp_info.names["cmake_find_package"] = "OpenAL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenAL"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]

        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "AL"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["AudioToolbox", "CoreAudio", "CoreFoundation"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ole32", "shell32", "User32"])
        if self._openal_cxx_backend and not self.options.shared:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
        if not self.options.shared:
            self.cpp_info.defines.append("AL_LIBTYPE_STATIC")
