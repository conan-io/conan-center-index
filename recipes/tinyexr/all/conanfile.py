from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, save
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class TinyExrConan(ConanFile):
    name = "tinyexr"
    description = "Tiny OpenEXR image loader/saver library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinyexr"
    topics = ("exr", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_z": ["zlib", "miniz"],
        "with_piz": [True, False],
        "with_zfp": [True, False],
        "with_thread": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "with_z": "miniz",
        "with_piz": True,
        "with_zfp": False,
        "with_thread": False,
        "with_openmp": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_z == "miniz":
            self.requires("miniz/3.0.2")
        else:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zfp:
            self.requires("zfp/1.0.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.options.with_thread and self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _extracted_license(self):
        content_lines = open(os.path.join(self.source_folder, "tinyexr.h")).readlines()
        license_content = []
        for i in range(3, 27):
            license_content.append(content_lines[i][:-1])
        return "\n".join(license_content)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extracted_license)
        copy(
            self,
            pattern="tinyexr.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.defines.append("TINYEXR_USE_MINIZ={}".format("1" if self.options.with_z == "miniz" else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_PIZ={}".format("1" if self.options.with_piz else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_ZFP={}".format("1" if self.options.with_zfp else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_THREAD={}".format("1" if self.options.with_thread else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_OPENMP={}".format("1" if self.options.with_openmp else "0"))

        if self.settings.os in ["Linux", "FreeBSD"] and self.options.with_thread:
            self.cpp_info.system_libs = ["pthread"]
