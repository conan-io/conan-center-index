import os
import argparse

from pylint import run_pylint

parser = argparse.ArgumentParser()
lint_group = parser.add_mutually_exclusive_group(required=True)
lint_group.add_argument("-r", "--recipe", action="store_true", default=False,
                        help="Lint conanfile.py")
lint_group.add_argument("-t", "--test", action="store_true", help="Lint test_package conanfile.py", default=False)
parser.add_argument('filenames', nargs="*", help="Filenames to potentially lint")
args = parser.parse_args()

# FIXME: The script always runs in the base folder for the repo,
# but we don't get proper linting if setting it here and needs to be set outside
# os.environ['PYTHONPATH'] = os.getcwd()

for file in args.filenames:
    if os.path.basename(file) == 'conanfile.py':
        dirname = os.path.dirname(file)
        if args.recipe and 'test_package' not in dirname:
            run_pylint(['--rcfile=linter/pylintrc_recipe', file])
        elif args.test and 'test_package' in dirname:
            run_pylint(['--rcfile=linter/pylintrc_testpackage', file])
