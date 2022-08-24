import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conans.tools import Version


class NanorangeConan(ConanFile):
    name = "nanorange"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tcbrindle/NanoRange"
    description = "NanoRange is a C++17 implementation of the C++20 Ranges proposals (formerly the Ranges TS)."
    topics = ("ranges", "C++17", "Ranges TS")
    no_copy_source = True
    settings = "compiler"
    options = {"deprecation_warnings": [True, False], "std_forward_declarations": [True, False]}
    default_options = {"deprecation_warnings": True, "std_forward_declarations": True}

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def configure(self):
        version = Version( self.settings.compiler.version )
        compiler = self.settings.compiler
        if self.settings.compiler.cppstd and \
           not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration("nanoRange requires at least c++17")
        elif compiler == "Visual Studio":
            if version < "16":
                raise ConanInvalidConfiguration("NanoRange requires at least Visual Studio version 15.9, please use 16")
            if not any([self.settings.compiler.cppstd == std for std in ["17", "20"]]):
                raise ConanInvalidConfiguration("nanoRange requires at least c++17")
        else:
            if ( compiler == "gcc" and version < "7" ) or ( compiler == "clang" and version < "5" ):
                raise ConanInvalidConfiguration("NanoRange requires a compiler that supports at least C++17")
            elif compiler == "apple-clang":
                self.output.warn("NanoRange is not tested with apple-clang")
                if version < "10":
                    raise ConanInvalidConfiguration("NanoRange requires a compiler that supports at least C++17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        commit = url[url.rfind("/")+1:url.find(".tar.gz")]
        extracted_folder = "NanoRange-" + commit
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy("LICENSE_1_0.txt", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if not self.options.deprecation_warnings:
            self.cpp_info.defines.append("NANORANGE_NO_DEPRECATION_WARNINGS")
        if not self.options.std_forward_declarations:
            self.cpp_info.defines.append("NANORANGE_NO_STD_FORWARD_DECLARATIONS")
