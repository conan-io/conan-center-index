import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class SigslotConan(ConanFile):
    name = "sigslot"
    description = "Sigslot is a header-only, thread safe implementation of signal-slots for C++."
    topics = ("signal", "slot", "c++14", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/palacaze/sigslot"
    license = "MIT"
    settings = "compiler", "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "15"  # 14 is not supported by the library
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "sigslot-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="signal.hpp", src=os.path.join(self._source_subfolder, "include", "sigslot"), dst=os.path.join("include", "sigslot"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "PalSigslot"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PalSigslot"
        self.cpp_info.names["cmake_find_package"] = "Pal"
        self.cpp_info.names["cmake_find_package_multi"] = "Pal"

        self.cpp_info.components["_sigslot"].libs = []
        self.cpp_info.components["_sigslot"].names["cmake_find_package"] = "Sigslot"
        self.cpp_info.components["_sigslot"].names["cmake_find_package_multi"] = "Sigslot"

        if self.settings.os == "Linux":
            self.cpp_info.components["_sigslot"].system_libs.append("pthread")
        if self.settings.os == "Windows":
            if self.settings.compiler in ("Visual Studio", "clang"):
                self.cpp_info.components["_sigslot"].exelinkflags.append('-OPT:NOICF')
