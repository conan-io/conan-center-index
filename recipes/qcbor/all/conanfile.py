from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir, load, save
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version

import os
import re

required_conan_version = ">=1.53.0"

class QCBORConan(ConanFile):
    name = "qcbor"
    description = "Comprehensive, powerful, commercial-quality CBOR encoder/decoder that is still suited for small devices."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/laurencelundblade/QCBOR"
    topics = ("serialization", "cbor", "rfc-7049", "rfc-8949")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_float": [False, "HW_USE", "PREFERRED", "ALL"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_float": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if Version(self.version) < "1.2":
            del self.options.disable_float

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")


    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "1.2":
            tc.variables["QCBOR_OPT_DISABLE_FLOAT_HW_USE"] = self.options.disable_float in ["HW_USE", "PREFERRED", "ALL"]
            tc.variables["QCBOR_OPT_DISABLE_FLOAT_PREFERRED"] = self.options.disable_float in ["PREFERRED", "ALL"]
            tc.variables["QCBOR_OPT_DISABLE_FLOAT_ALL"] = self.options.disable_float == "ALL"
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # Extract the License/s from README.md to a file
        tmp = load(self, os.path.join(self.source_folder, "inc", "qcbor", "qcbor.h"))
        license_contents = re.search("( Copyright.*) =====", tmp, re.DOTALL)[1]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package_info(self):
        self.cpp_info.libs = ["qcbor"]
        if self.settings.os in ["Linux", "FreeBSD"] and \
            (Version(self.version) < "1.2" or self.options.disable_float == False):
            self.cpp_info.system_libs.append("m")
