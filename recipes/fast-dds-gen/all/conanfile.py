import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.2"


class FastDdsGenConan(ConanFile):
    name = "fast-dds-gen"
    description = "eProsima Fast DDS IDL Code Generator"
    license = "Apache-2.0"
    homepage = "https://github.com/eProsima/Fast-DDS-Gen"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("idl", "code-generation", "fastdds")

    package_type = "application"
    settings = "os", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openjdk/19.0.2")

    def build_requirements(self):
        self.tool_requires("openjdk/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0], strip_root=True)
        get(self, **self.conan_data["sources"][self.version][1], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        with chdir(self, self.source_folder):
            run_prefix = ""
            if self.settings_build.os != "Windows":
                self.run("chmod +x gradlew")
                run_prefix = "./"

            self.run(f"{run_prefix}gradlew assemble")

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.jar",
            src=os.path.join(self.source_folder, "share"),
            dst=os.path.join(self.package_folder, "share"),
            keep_path=True,
        )
        copy(
            self,
            "*",
            src=os.path.join(self.source_folder, "scripts"),
            dst=os.path.join(self.package_folder, "bin"),
            keep_path=False,
        )

        for script in os.listdir(os.path.join(self.package_folder, "bin")):
            script_path = os.path.join(self.package_folder, "bin", script)
            if os.path.isfile(script_path):
                os.chmod(script_path, 0o755)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.set_property("cmake_file_name", "fastddsgen")
        self.cpp_info.set_property("cmake_target_name", "fastddsgen::fastddsgen")

        fastdds_version = self.conan_data.get("fastdds_versions", {}).get(str(self.version), "3.2.1")
        self.conf_info.define("user.fast-dds-gen:fastdds_version", fastdds_version)
