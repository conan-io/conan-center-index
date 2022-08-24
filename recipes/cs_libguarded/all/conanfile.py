import os
from conan import ConanFile, tools$


class CsLibguardedConan(ConanFile):
    name = "cs_libguarded"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/copperspice/libguarded"
    description = "The libGuarded library is a standalone header-only library for multithreaded programming."
    topics = ("multithreading", "templates", "cpp14", "mutexes")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "cs_libguarded-libguarded-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp",  dst='include', src=os.path.join(self._source_subfolder, "src"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
