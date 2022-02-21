import os
import yaml
import packaging.version
import subprocess



def main():
    packages = set()
    files = subprocess.run(["git", "show", "--first-parent", "--name-only", r'--pretty="format:%n"'], capture_output=True, text=True)
    for line in files.stdout.splitlines():
        parts = line.split("/")
        if len(parts) >= 4:
            packages.add(parts[1] + "/" + parts[2])
    for line in packages:
        package = line.split("/")[0]
        version = None
        folder = line.split("/")[1]
        with open(os.path.join("recipes", package, "config.yml"), "r") as file:
            config = yaml.safe_load(file)
            for v in config["versions"]:
                if config["versions"][v]["folder"] != folder:
                    continue
                try:
                    if not version or packaging.version.Version(v) > packaging.version.Version(version):
                        version = v
                except packaging.version.InvalidVersion:
                    print("Error parsing version %s for package %s" % (v, package))

        if version:
            command = ["conan", "export", os.path.join("recipes", package, folder), "%s/%s@" % (package, version)]
            p = subprocess.run(command, check=False)

if __name__ == "__main__":
    # execute only if run as a script
    main()
