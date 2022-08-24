from conans import ConanFile, tools
import os


class ArgparseConan(ConanFile):
    name = "argh"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/adishavit/argh"
    topics = ("conan", "argh", "argument", "parsing")
    license = "BSD-3"
    description = "Frustration-free command line processing"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("argh-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("argh.h", src=self._source_subfolder, dst=os.path.join("include", "argh"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "argh"))
