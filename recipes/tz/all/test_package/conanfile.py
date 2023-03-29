from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
import json
import os


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def generate(self):
        # Save dependencies to dependencies.json for consumption in test()
        deps = {"tz": {key: value == "True" for key, value in self.dependencies["tz"].options.items()}}
        with open('dependencies.json', 'w') as f:
            f.write(json.dumps(deps))

    def test(self):
        if not cross_building(self):
            # Read dependency options in from dependencies.json
            # This is achievable in conan >2.0 using self.dependencies["tz"].options.data_only,
            # however this is not a cross-version compatible approach and so this is used
            # while support for conan 1.x is ongoing.
            deps = {}
            with open(os.path.join(self.generators_folder, 'dependencies.json'), 'r') as f:
                deps = json.loads(f.read())

            if not deps["tz"]["data_only"]:
                which = "where" if self.settings.os == "Windows" else "which"
                cmd = f"{which} zdump"
                self.output.info(f"Executing '{cmd}'")
                self.run(cmd, env="conanrun")

                cmd = "zdump -v America/Los_Angeles"
                self.output.info(f"Executing '{cmd}'")
                self.run(cmd, env="conanrun")

            self.output.info("Test that tzdata is readable")
            cmd = "python -c 'import os; tzdata = os.environ[\"TZDATA\"]; f=open(os.path.join(tzdata, \"factory\"), \"r\"); s = f.read(); f.close(); print(s)'"
            self.run(cmd, env="conanrun")
