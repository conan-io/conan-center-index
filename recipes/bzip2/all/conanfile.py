from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, save
import os
import textwrap

required_conan_version = ">=1.46.0"


class Bzip2Conan(ConanFile):
    name = "bzip2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bzip.org"
    license = "bzip2-1.0.8"
    description = "bzip2 is a free and open-source file compression program that uses the Burrows Wheeler algorithm."
    topics = ("bzip2", "data-compressor", "file-compression")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executable": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executable": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.license = "bzip2-{}".format(self.version)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BZ2_VERSION_STRING"] = self.version
        tc.variables["BZ2_VERSION_MAJOR"] = self.version.split(".")[0]
        tc.variables["BZ2_BUILD_EXE"] = self.options.build_executable
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            set(BZIP2_NEED_PREFIX TRUE)
            if(NOT DEFINED BZIP2_FOUND AND DEFINED BZip2_FOUND)
                set(BZIP2_FOUND ${BZip2_FOUND})
            endif()
            if(NOT DEFINED BZIP2_INCLUDE_DIRS AND DEFINED BZip2_INCLUDE_DIRS)
                set(BZIP2_INCLUDE_DIRS ${BZip2_INCLUDE_DIRS})
            endif()
            if(NOT DEFINED BZIP2_INCLUDE_DIR AND DEFINED BZip2_INCLUDE_DIR)
                set(BZIP2_INCLUDE_DIR ${BZip2_INCLUDE_DIR})
            endif()
            if(NOT DEFINED BZIP2_LIBRARIES AND DEFINED BZip2_LIBRARIES)
                set(BZIP2_LIBRARIES ${BZip2_LIBRARIES})
            endif()
            if(NOT DEFINED BZIP2_VERSION_STRING AND DEFINED BZip2_VERSION)
                set(BZIP2_VERSION_STRING ${BZip2_VERSION})
            endif()
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "BZip2")
        self.cpp_info.set_property("cmake_target_name", "BZip2::BZip2")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.libs = ["bz2"]

        self.cpp_info.names["cmake_find_package"] = "BZip2"
        self.cpp_info.names["cmake_find_package_multi"] = "BZip2"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]

        if self.options.build_executable:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
