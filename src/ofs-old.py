import argparse
import logging
import json
import os
import yaml

import downloader
import patcher
import log_helper


parser = argparse.ArgumentParser(description='clone and manipulate git repositories')
parser.add_argument('--input-file', metavar='<input_file>',
                    dest='input_file', required=True,
                    help='Input file including information like package lists and target version.')
parser.add_argument('--config-file', metavar='<config_file>',
                    dest='config_file', required=True,
                    help='Configuration file for the software, including working dir, number of workers etc.')


def parse_input_file(input_file):
    if not input_file:
        raise Exception

    with open(input_file, 'r') as inputs:
        input_dict = json.load(inputs)

    package_list = input_dict["PackageLists"]
    target_release = input_dict["TargetRelease"]
    return package_list, target_release


if __name__ == "__main__":
    parsed_args = parser.parse_args()
    with open(parsed_args.config_file, 'r') as config_file:
        config_options = yaml.load(config_file, Loader=yaml.SafeLoader)

    if not os.path.exists(config_options['WorkingDir']):
        os.makedirs(config_options['WorkingDir'])

    logger = log_helper.Logger(config_options['LoggingDir'], logging.ERROR, logging.DEBUG)

    pkg_list, tgt_release = parse_input_file(parsed_args.input_file)
    downloader.clone_and_checkout(pkg_list, tgt_release, config_options['WorkingDir'], logger)
    downloader.tar_extract(pkg_list, config_options['WorkingDir'], logger)
    patcher.handling_patches(pkg_list, config_options['WorkingDir'], logger)
