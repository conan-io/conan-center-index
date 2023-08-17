import os
from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version


class DbgMacroConan(ConanFile):
    name = "dbg-macro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sharkdp/dbg-macro"
    license = "MIT"
    description = "A dbg(...) macro for C++"
    topics = ("debugging", "macro", "pretty-printing", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.settings.compiler.get_safe('cppstd'):
            check_min_cppstd(self, 17)

        min_versions = {
            "gcc": 8
        }

        compiler = self.settings.compiler
        if str(compiler) in min_versions and Version(compiler.version) < min_versions[str(compiler)]:
            raise ConanInvalidConfiguration("dbg-macro requires C++17 which your compiler does not support.")

    def package(self):
        copy(self, "dbg.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_id(self):
        self.info.clear()
