from conans import ConanFile, tools
import glob
import os


class Fp16Conan(ConanFile):
    name = "fp16"
    description = "Conversion to/from half-precision floating point formats."
    license = "MIT"
    topics = ("conan", "fp16", "half-precision-floating-point")
    homepage = "https://github.com/Maratyszcza/FP16"
    url = "https://github.com/conan-io/conan-center-index"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("psimd/cci.20200517")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("FP16-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
