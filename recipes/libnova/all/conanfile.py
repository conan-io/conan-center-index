from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os
import requests

required_conan_version = ">=1.53.0"


class LibnovaConan(ConanFile):
    name = "libnova"
    description = (
        "libnova is a general purpose, double precision, celestial mechanics, "
        "astrometry and astrodynamics library."
    )
    license = "LGPL-2.0-only"
    topics = ("celestial-mechanics", "astrometry", "astrodynamics")
    homepage = "https://sourceforge.net/projects/libnova"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @staticmethod
    def _generate_git_tag_archive_sourceforge(url, timeout=10, retry=2):
        def try_post(retry_count):
            try:
                requests.post(url, timeout=timeout)
            except:
                if retry_count < retry:
                    try_post(retry_count + 1)
                else:
                    raise ConanException("All the attempt to generate archive url have failed.")
        try_post(0)

    def source(self):
        # Generate the archive download link
        self._generate_git_tag_archive_sourceforge(self.conan_data["sources"][self.version]["post"]["url"])

        # Download archive
        get(self, **self.conan_data["sources"][self.version]["archive"], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBRARY"] = self.options.shared
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

    def package_info(self):
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"nova{postfix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
