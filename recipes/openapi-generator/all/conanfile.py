from conan import ConanFile
from conan.tools.files import copy, download, save
from conan.tools.scm import Version
import os


required_conan_version = ">=1.47.0"


class OpenApiGeneratorConan(ConanFile):
    name = "openapi-generator"
    description = "Generation of API client libraries (SDK generation), server stubs, documentation and configuration automatically given an OpenAPI Spec (v2, v3)"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openapi-generator.tech"
    topics = ("api", "sdk", "generator", "openapi")
    settings = "os", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        pass

    def build(self):
        v = self.conan_data["sources"][self.version]
        download(
                self,
                url=v["url"],
                filename=os.path.join(self.source_folder, "openapi-generator.jar"),
                sha256=v["sha256"],
                )
        download(
                self,
                url="https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/LICENSE",
                filename=os.path.join(self.source_folder, "LICENSE"),
                sha256="91a2fcdfc23cbd1188a22cc3b76647bf6eb05c87889e376a19fe478f0398ff02",
                )

    def package(self):
        # a license file is always mandatory
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="openapi-generator.jar", dst=os.path.join(self.package_folder, "res"), src=self.source_folder)
        jar = os.path.join(self.package_folder, "res", "openapi-generator.jar")
        if self.info.settings.os == "Windows":
            save(self,
                 path=os.path.join(self.package_folder, "bin", "openapi-generator.bat"),
                 content=f"""\
                         java -jar {jar} %*
                         """
                 )
        else:
            save(self,
                 path=os.path.join(self.package_folder, "bin", "openapi-generator"),
                 content=f"""\
                         #!/bin/bash
                         java -jar {jar} $@
                         """
                 )

    def package_info(self):
        # folders not used for pre-built binaries
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
