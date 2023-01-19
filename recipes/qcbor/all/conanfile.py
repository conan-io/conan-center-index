from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir, load, save
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os
import re

required_conan_version = ">=1.52.0"

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
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
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
