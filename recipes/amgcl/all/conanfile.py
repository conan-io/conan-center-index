from conan import ConanFile, tools
from conans import CMake
import os


class UncrustifyConan(ConanFile):
    name = "amgcl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ddemidov/amgcl"
    topics = ("mathematics", "opencl", "openmp", "cuda", "amg")
    license = "MIT"
    description = "AMGCL is a header-only C++ library for solving large sparse linear systems with algebraic multigrid (AMG) method."
    settings = "compiler"
    no_copy_source = True
    requires = [("boost/1.76.0")]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        self.copy("*",
                  dst=os.path.join("include", "amgcl"),
                  src=(os.path.join(self._source_subfolder, "amgcl")))

    def package_id(self):
        self.info.header_only()
