import os
import argparse
import sys

parser = argparse.ArgumentParser()

lint_group = parser.add_mutually_exclusive_group(required=True)
lint_group.add_argument("-r", "--recipe", action="store_true", default=False,
                        help="Lint conanfile.py")
lint_group.add_argument("-t", "--test", action="store_true", help="Lint test_package conanfile.py", default=False)
lint_group.add_argument("-yl", "--yamllint", action="store_true", help="Lint yaml files", default=False)
lint_group.add_argument("-ys", "--yamlscheme", action="store_true", help="Lint yaml scheme", default=False)

parser.add_argument('filenames', nargs="*", help="Filenames to potentially lint")
args = parser.parse_args()

for file in args.filenames:
    basename = os.path.basename(file)
    if basename == 'conanfile.py':
        # The recipe linters need access to the files in cci
        sys.path.append(os.getcwd())
        dirname = os.path.dirname(file)
        if args.recipe and 'test_package' not in dirname:
            from pylint import run_pylint
            run_pylint(['--rcfile=linter/pylintrc_recipe', file])
        elif args.test and 'test_package' in dirname:
            from pylint import run_pylint
            run_pylint(['--rcfile=linter/pylintrc_testpackage', file])
    elif basename.endswith('.yml') or basename.endswith('.yaml'):
        if args.yamllint:
            from yamllint.cli import run
            run([file, '--config-file', 'linter/yamllint_rules.yml', '-f', 'standard'])
        elif args.yamlscheme:
            if basename == "config.yml":
                from config_yaml_linter import main
                main([file])
            elif basename == "conandata.yml":
                from conandata_yaml_linter import main
                main([file])
