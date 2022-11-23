from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.52.0"


class LibaecConan(ConanFile):
    name = "libaec"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.dkrz.de/k202009/libaec"
    description = "Adaptive Entropy Coding library"
    topics = "dsp", "encoding", "decoding"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
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

    def validate(self):
        if Version(self.version) >= "1.0.6" and is_msvc(self):
            # libaec/1.0.6 uses "restrict" keyword which seems to be supported since Visual Studio 16.
            if Version(self.settings.compiler.version) < "16":
                raise ConanInvalidConfiguration("{} does not support Visual Studio {}".format(self.name, self.settings.compiler.version))
            # In libaec/1.0.6, fail to build aec_client command with debug and shared settings in Visual Studio.
            # Temporary, this recipe doesn't support these settings.
            if self.options.shared and self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration("{} does not support debug and shared build in Visual Studio(currently)".format(self.name))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if Version(self.version) < "1.0.6":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "add_subdirectory(tests)", "")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        if Version(self.version) < "1.0.6":
            copy(self, pattern="Copyright.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        else:
            copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        aec_name = "aec"
        if self.settings.os == "Windows" and Version(self.version) >= "1.0.6" and not self.options.shared:
            aec_name = "aec_static" 
        szip_name = "sz"
        if self.settings.os == "Windows":
            if Version(self.version) >= "1.0.6":
                szip_name = "szip" if self.options.shared else "szip_static"
            elif self.options.shared:
                szip_name = "szip"
        self.cpp_info.libs = [szip_name, aec_name]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
