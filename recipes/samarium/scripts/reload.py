#!/usr/bin/env python

import sys
import os
import subprocess
from time import sleep, time
import json
import pathlib


def process(git_command_list):
    return [os.path.abspath(x) for x in subprocess.run(git_command_list, capture_output=True).stdout.decode()[:-1].splitlines()]


def get_files(input_path, git):
    if git:
        new = process(['git', 'ls-files'])
        old = process(['git', 'ls-files', '-o', '--exclude-standard'])
        deleted = process(['git', 'ls-files', '-d'])
        return [i for i in sorted(new + old) if i not in deleted]
    else:
        output = []
        for folder, subfolders, files in os.walk(input_path):
            for file in files:
                output.append(os.path.abspath(os.path.join(folder, file)))
        return output


def get_dict(input_files):
    return {i: os.path.getmtime(i) for i in input_files}


def get(input_path, git):
    files = get_files(input_path, git)
    times = get_dict(files)
    return files, times


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    options = {
        'root_dir': os.getcwd(),
        'commands': {},
        'delay_seconds': 0.005,
        'exit_on_error': False,
        'clear_screen': True,
        "use_gitignore": True
    }

    options_path = os.path.join(pathlib.Path(
        __file__).parent.resolve(), 'reload.json')
    if len(sys.argv) > 1:
        options_path = sys.argv[1]
    with open(options_path) as options_file:
        options.update(json.load(options_file))
    if not os.path.isdir(options['root_dir']):
        raise FileNotFoundError(f'{options["root_dir"]} does not exist')

    options['root_dir'] = os.path.abspath(options['root_dir'])
    os.chdir(options['root_dir'])

    def run(command):
        subprocess.run(command, shell=True, check=options['exit_on_error'])

    if 'pre' in options['commands']:
        for command in options['commands']['pre']:
            run(command)

    for command in options['commands']['all']:
        run(command)
    files, times = get(options['root_dir'], options["use_gitignore"])

    try:
        while True:
            sleep(options['delay_seconds'])
            new_files, new_times = get(
                options['root_dir'], options["use_gitignore"])
            if new_times == times:
                continue
            if options['clear_screen']:
                clear_screen()

            if 'structure' in options['commands'] and new_files != files:
                for command in options['commands']['structure']:
                    run(command)
            if 'all' in options['commands']:
                for command in options['commands']['all']:
                    run(command)

            files = new_files
            times = new_times
    except KeyboardInterrupt:
        pass
