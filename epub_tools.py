#!/usr/bin/env python3
# -- coding: utf-8

import argparse
import subprocess
import os
from pathlib import Path
from zipfile import ZipFile

special_dirs = ['OEBPS', 'META-INF']

def create_epub(opf_file, epub_name, should_open):
    print('creating epub with name {}'.format(epub_name))
    opf_path = Path(opf_file).expanduser()
    if opf_path.exists() and opf_path.suffix == '.opf':
        print("opf file is here, checking structure")
    else:
        raise Exception('Please provide a valid path to an .opf file')

    base_path = opf_path.parent.parent
    print('base path for compressing: ' + str(base_path.resolve()))
    if (not (base_path / "OEBPS").is_dir()):
        raise Exception("directory \"OEBPS\" not found, aborting")
    if (not (base_path / "META-INF").is_dir()):
        raise Exception("\"META-INF\" path not found, aborting")
    if (not (base_path / "mimetype").is_file()):
        raise Exception("\"mimetype\" file not found, aborting")

#     // To zip up an epub:
# 1. zip -X MyNewEbook.epub mimetype
# 2. zip -rg MyNewEbook.epub META-INF -x \*.DS_Store
# 3. zip -rg MyNewEbook.epub OEBPS -x \*.DS_Store

    print('Structure is correct, proceding...')
    final_epub_path = base_path / (epub_name + '.epub')

    with ZipFile(final_epub_path, 'w') as zip:
        zip.write(base_path / 'mimetype', 'mimetype')
        for special_dir in special_dirs:
            from_path = base_path / special_dir
            for root, dirs, files in os.walk(from_path):
                root_path = Path(root)
                rel_dir = root_path.relative_to(
                    os.path.commonpath([root_path, base_path]))
                zip.write(root_path, arcname=rel_dir)
                for file in files:
                    if (file.startswith('.')):
                        continue
                    zip.write(root_path / file, arcname=rel_dir / file)
    print('Success! epub written in ->' + str(final_epub_path))
    if (should_open):
       subprocess.run(["open", final_epub_path])


def extract_epub(epub_name, extract_path, should_open):
    print('extracting {} in {}'.format(epub_name, extract_path))
    with ZipFile(epub_name) as zip:
        zip.extractall(path=extract_path)
    print('Success!')
    if should_open:
        subprocess.run(["open", extract_path])


def parse_args():
    """ Defines commandline arguments and options accepted by this script. """
    parser = argparse.ArgumentParser(
        description='EPUB packaging tools. Create or extract epub files to manipulate files')
    cmd_choices = ['make', 'extract']
    parser.add_argument('cmd', type=str, choices=cmd_choices,
                        help='command to create an epub from a valid tree structure or to extract the contents of the epub file for manipulation')
    parser.add_argument('input', type=str,
                        help='Path to .opf file to package or to the .epub file to extract')
    parser.add_argument('target', type=str, default=None,
                        help='Name of target file. If a path to a folder is given, it will output the result to that path')
    parser.add_argument('-o', "--open", action='store_true',
                        help='Open resulting target ')

    args = parser.parse_args()
    for cmd in cmd_choices:
        setattr(args, cmd, False)
    setattr(args, args.cmd, True)
    return args


if __name__ == "__main__":
    args = parse_args()
    if (args.extract):
        name = args.target if args.target is not None else args.input
        output_path = name if os.path.isdir(name) else Path(name).parent
        extract_epub(args.input, output_path, args.open)
    elif (args.make):
        if (args.target is None):
            raise Exception('You must provide a name for the .epub to package')
        create_epub(args.input, args.target, args.open)
