from conan import ConanFile, tools$
import glob
import os


class PsimdConan(ConanFile):
    name = "psimd"
    description = "Portable 128-bit SIMD intrinsics."
    license = "MIT"
    topics = ("conan", "psimd", "simd")
    homepage = "https://github.com/Maratyszcza/psimd"
    url = "https://github.com/conan-io/conan-center-index"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("psimd-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
