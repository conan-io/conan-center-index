import os
from conans import ConanFile, tools


class TinyExrConan(ConanFile):
    name = "tinyexr"
    description = "Tiny OpenEXR image loader/saver library"
    homepage = "https://github.com/syoyo/tinyexr"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    topics = ("conan", "exr", "header-only")
    exports_sources = ["patches/*"]
    settings = "os"
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

    def requirements(self):
        if self.options.with_z == "miniz":
            self.requires("miniz/2.1.0")
        else:
            self.requires("zlib/1.2.11")
        if self.options.with_zfp:
            self.requires("zfp/0.5.5")

    def configure(self):
        if self.options.with_thread and self.settings.compiler.get_safe("cppstd") :
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _extracted_license(self):
        content_lines = open(os.path.join(self.source_folder, self._source_subfolder, "tinyexr.h")).readlines()
        license_content = []
        for i in range(3, 27):
            license_content.append(content_lines[i][:-1])
        return "\n".join(license_content)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extracted_license)
        self.copy("tinyexr.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.defines.append("TINYEXR_USE_MINIZ=" + ( "1" if self.options.with_z == "miniz" else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_PIZ=" + ( "1" if self.options.with_piz else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_ZFP=" + ( "1" if self.options.with_zfp else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_THREAD=" + ( "1" if self.options.with_zfp else "0"))
        self.cpp_info.defines.append("TINYEXR_USE_OPENMP=" + ( "1" if self.options.with_zfp else "0"))

        if self.settings.os == "Linux" and self.options.with_thread:
            self.cpp_info.system_libs = ["pthread"]
