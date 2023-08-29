import os
import shutil
import tarfile
from fnmatch import fnmatch

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, download, export_conandata_patches, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class FruitConan(ConanFile):
    name = "fruit"
    description = "C++ dependency injection framework"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/fruit"
    license = "Apache-2.0"
    topics = ("injection", "framework")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_boost": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_boost": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.83.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, "11")
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimal_version = {
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "7.3",
            "Visual Studio": "14"
        }

        if compiler in minimal_version and \
           compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports"
                                            " at least C++11. {compiler} {compiler_version} is not"
                                            " supported.")

    def source(self):
        if Version(self.version) == "3.4.0":
            filename = os.path.basename(self.conan_data["sources"][self.version]["url"])
            download(self, filename=filename, **self.conan_data["sources"][self.version])
            extracted_dir = self.name + "-" + self.version

            with tarfile.TarFile.open(filename, 'r:*') as tarredgzippedFile:
                # NOTE: In fruit v3.4.0, The archive file contains the file names
                # build and BUILD in the extras/bazel_root/third_party/fruit directory.
                # Extraction fails on a case-insensitive file system due to file
                # name conflicts.
                # Exclude build as a workaround.
                exclude_pattern = f"{extracted_dir}/extras/bazel_root/third_party/fruit/build"
                members = list(filter(lambda m: not fnmatch(m.name, exclude_pattern),
                                    tarredgzippedFile.getmembers()))
                tarredgzippedFile.extractall(path=self.source_folder, members=members)
            allfiles = os.listdir(os.path.join(self.source_folder, extracted_dir))
            for file_name in allfiles:
                shutil.move(os.path.join(self.source_folder, extracted_dir, file_name), self.source_folder)
        else:
            get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FRUIT_USES_BOOST"] = self.options.with_boost
        tc.variables["FRUIT_ENABLE_COVERAGE"] = False
        tc.variables["RUN_TESTS_UNDER_VALGRIND"] = False
        tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fruit"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
