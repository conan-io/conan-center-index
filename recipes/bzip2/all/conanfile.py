import os
import textwrap
from conans import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.layout import cmake_layout

required_conan_version = ">=1.38.0"


class Bzip2Conan(ConanFile):
    name = "bzip2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bzip.org"
    license = "bzip2-1.0.8"
    description = "bzip2 is a free and open-source file compression program that uses the Burrows Wheeler algorithm."
    topics = ("bzip2", "data-compressor", "file-compression")

    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executable": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executable": True
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.license = "bzip2-{}".format(self.version)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        # FIXME: this is failing after the export export to "src" in local folder
        try:
            os.rename("CMakeLists.txt", "src/CMakeLists.txt")
        except:
            pass

    def layout(self):
        cmake_layout(self)

    def generate(self):
        cmake_toolchain = CMakeToolchain(self)
        cmake_toolchain.variables["BZ2_VERSION_STRING"] = self.version
        cmake_toolchain.variables["BZ2_VERSION_MAJOR"] = tools.Version(self.version).major
        cmake_toolchain.variables["BZ2_BUILD_EXE"] = self.options.build_executable
        cmake_toolchain.generate()

    def build(self):
        tools.files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses")
        cmake = CMake(self)
        cmake.install()
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            if(DEFINED BZip2_FOUND)
                set(BZIP2_FOUND ${BZip2_FOUND})
                set(BZIP2_NEED_PREFIX TRUE)
            endif()
            if(DEFINED BZip2_INCLUDE_DIR)
                set(BZIP2_INCLUDE_DIRS ${BZip2_INCLUDE_DIR})
                set(BZIP2_INCLUDE_DIR ${BZip2_INCLUDE_DIR})
            endif()
            if(DEFINED BZip2_LIBRARIES)
                set(BZIP2_LIBRARIES ${BZip2_LIBRARIES})
            endif()
            if(DEFINED BZip2_VERSION)
                set(BZIP2_VERSION_STRING ${BZip2_VERSION})
            endif()
        """)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-variables.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [os.path.join(self._module_subfolder, self._module_file)]
        self.cpp_info.libs = ["bz2"]
        self.cpp_info.set_property("cmake_file_name", "BZip2")
        self.cpp_info.set_property("cmake_target_name", "BZip2")
