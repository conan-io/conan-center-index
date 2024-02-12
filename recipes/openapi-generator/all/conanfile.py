from conan import ConanFile
from conan.tools.files import copy, download, save
import os
import stat


required_conan_version = ">=1.47.0"


class OpenApiGeneratorConan(ConanFile):
    name = "openapi-generator"
    description = "Generation of API client libraries (SDK generation), server stubs, documentation and configuration automatically given an OpenAPI Spec (v2, v3)"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openapi-generator.tech"
    topics = ("api", "sdk", "generator", "openapi")
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def requirements(self):
        self.requires("openjdk/19.0.2")

    def package_id(self):
        del self.info.settings.arch
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
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="openapi-generator.jar", dst=os.path.join(self.package_folder, "res"), src=self.source_folder)
        if self.settings.os == "Windows":
            save(self,
                 path=os.path.join(self.package_folder, "bin", "openapi-generator.bat"),
                 content="""\
                         java -classpath %CLASSPATH% org.openapitools.codegen.OpenAPIGenerator %*
                         """
                 )
        else:
            bin_path = os.path.join(self.package_folder, "bin", "openapi-generator")
            save(self,
                 path=bin_path,
                 content="""\
                         #!/bin/bash
                         java -classpath $CLASSPATH org.openapitools.codegen.OpenAPIGenerator $@
                         """
                 )
            st = os.stat(bin_path)
            os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

    def package_info(self):
        # folders not used for pre-built binaries
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
        jar = os.path.join(self.package_folder, "res", "openapi-generator.jar")
        self.runenv_info.prepend_path("CLASSPATH", jar)

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.CLASSPATH.append(jar)
