import os
from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration


class DbgMacroConan(ConanFile):
    name = "dbg-macro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sharkdp/dbg-macro"
    license = "MIT"
    description = "A dbg(...) macro for C++"
    topics = ("conan", "debugging", "macro", "pretty-printing", "header-only")
    settings = ("compiler", )
    no_copy_source = True


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def configure(self):
        if self.settings.compiler == "gcc" and int(f"{self.settings.compiler.version}") < 5:
            raise ConanInvalidConfiguration(
                "dbg-macro can't be used by {0} {1}".format(
                    self.settings.compiler,
                    self.settings.compiler.version
                )
            )

    def package(self):
        copy(self, "dbg.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_id(self):
        self.info.clear()
