import os
from conan import ConanFile, tools
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration


class ZugConan(ConanFile):
    name = "zug"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sinusoid.es/zug/"
    description = "Transducers for C++ — Clojure style higher order push/pull \
        sequence transformations"
    topics = ("transducer", "algorithm", "signals")
    settings = ("compiler", "arch", "os", "build_type")
    no_copy_source = True

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder
        )

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "14")

        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warn("Unknown compiler, assuming it supports at least C++14")
            return

        version = tools.scm.Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports at least C++14")

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        self.copy(pattern="*.hpp", dst=os.path.join("include", "zug"), src=os.path.join(self.source_folder, "zug"))

    def package_info(self):
        if is_msvc(self):
            self.cpp_info.cxxflags = ["/Zc:externConstexpr"]

