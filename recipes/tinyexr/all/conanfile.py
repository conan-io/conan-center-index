from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class TinyExrConan(ConanFile):
    name = "tinyexr"
    description = "Tiny OpenEXR image loader/saver library"
    homepage = "https://github.com/syoyo/tinyexr"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    topics = ("exr", "header-only")

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        if self.options.with_z == "miniz":
            self.requires("miniz/2.2.0")
        else:
            self.requires("zlib/1.2.12")
        if self.options.with_zfp:
            self.requires("zfp/0.5.5")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.options.with_thread and self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _extracted_license(self):
        content_lines = open(os.path.join(self.source_folder, self._source_subfolder, "tinyexr.h")).readlines()
        license_content = []
        for i in range(3, 27):
            license_content.append(content_lines[i][:-1])
        return "\n".join(license_content)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extracted_license)
        self.copy("tinyexr.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.defines.append("TINYEXR_USE_MINIZ={}".format("1" if self.options.with_z == "miniz" else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_PIZ={}".format("1" if self.options.with_piz else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_ZFP={}".format("1" if self.options.with_zfp else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_THREAD={}".format("1" if self.options.with_thread else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_OPENMP={}".format("1" if self.options.with_openmp else "0"))

        if self.settings.os in ["Linux", "FreeBSD"] and self.options.with_thread:
            self.cpp_info.system_libs = ["pthread"]
