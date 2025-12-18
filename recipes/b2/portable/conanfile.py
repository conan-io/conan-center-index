from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

import os


required_conan_version = ">=2.0"


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://www.bfgroup.xyz/b2/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("installer", "builder", "build", "build-system")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler"
    package_type = "application"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        if cross_building(self):
            self.tool_requires(f"b2/{self.version}")

    @property
    def _b2_engine_dir(self):
        return os.path.join(self.source_folder, "src", "engine")

    @property
    def _b2_output_dir(self):
        return os.path.join(self.build_folder, "output")

    def build(self):
        # The order of the with:with: below is important. The first one changes
        # the current dir. While the second does env changes that guarantees
        # that dir doesn't change if/when vsvars runs to set the msvc compile
        # env.
        self.output.info("Build engine...")
        if is_msvc(self):
            command = "build.bat msvc"
        else:
            flags = []
            if self.settings.os == "Linux":
                flags.append("-lpthread")
            if self.settings.compiler == "gcc":
                flags.extend(["-static-libstdc++", "-static-libgcc"])

            command = "./build.sh cxx"
            if flags:
                command += f" --cxxflags='{' '.join(flags)}'"

        if self.conf.get("tools.build:compiler_executables"):
            cxx_compiler = self.conf.get("tools.build:compiler_executables").get("cpp")
        else:
            cxx_compiler = None

        if cxx_compiler:
            self.output.info(f"Using C++ compiler: {cxx_compiler}")
            command += f" --cxx={cxx_compiler}"

        with chdir(self, self._b2_engine_dir):
            self.run(command)

        self.output.info("Install...")
        if cross_building(self):
            # use the pre-built b2 from the tool_requires
            b2_command = "b2"
        else:
            b2_command = os.path.join(self._b2_engine_dir, "b2.exe" if self.settings.os == "Windows" else "b2")
        install_command = \
            (f"{b2_command} --ignore-site-config " +
             f"--prefix={self._b2_output_dir} " +
             "--abbreviate-paths " +
             "install " +
             "b2-install-layout=portable")
        with chdir(self, self.source_folder):
            self.run(install_command)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.LICENSE", src=self._b2_engine_dir, dst=os.path.join(self.package_folder, "licenses"))

        bin_dir = os.path.join(self.package_folder, "bin")
        copy(self, "*b2", dst=bin_dir, src=self._b2_output_dir)
        copy(self, "*b2.exe", dst=bin_dir, src=self._b2_output_dir)
        copy(self, "*.jam", dst=bin_dir, src=self._b2_output_dir)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []