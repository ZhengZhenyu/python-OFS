import argparse
import logging
import json
import os
import subprocess
import yaml

import log_helper

parser = argparse.ArgumentParser(description='clone and manipulate git repositories')
parser.add_argument('--package-list', metavar='<package_list>',
                    dest='package_list', required=True,
                    help='Input file including information like package lists and target version.')
parser.add_argument('--config-file', metavar='<config_file>',
                    dest='config_file', required=True,
                    help='Configuration file for the software, including working dir, number of workers etc.')


def parse_package_list(list_file):
    if not list_file:
        raise Exception

    with open(list_file, 'r') as inputs:
        input_dict = json.load(inputs)

    package_list = input_dict["PackageList"]
    return package_list


def create_install_img(config_options, buildarch, iso_dir):
    print("Calling Lorax ...")
    cmd = ['lorax', '--isfinal', '-p', str(config_options['ProductName']),
           '-v', str(config_options['ProductVersion']),
           '-r', str(config_options['ProductRelease']),
           '-t', str(config_options['ProductVariant']),
           '--sharedir', '../etc/80-openeuler', '--rootfs-size=4',
           '--buildarch=' + buildarch,
           '-s', config_options['UpstreamRepo'],
           '--nomacboot', '--noupgrade',
           '--logfile', config_options['LogPath'] + '/lorax.log',
           iso_dir]
    return subprocess.run(cmd)


def create_repos(config_options):
    print('Creating Repos ...')
    if os.path.exists('/etc/yum.repos.d'):
        os.system('rm -rf repos.old && mv /etc/yum.repos.d /etc/repos.old && mkdir -p /etc/yum.repos.d/')
        os.system('yum-config-manager  --add-repo ' + config_options['UpstreamRepo'])
        os.system('yum clean all')


def cleanup(config_options):
    print('Cleanup ...')
    os.system('rm -rf /etc/yum.repos.d && mv /etc/repos.old /etc/yum.repos.d')


def download_rpms(download_list, config_options, iso_dir):
    cmd = ['yumdownloader', '--resolve', '--installroot=' + config_options['WorkingDir'] + '/tmp',
           '--destdir=' + iso_dir + '/Packages/',
           ' '.join(download_list)]
    os.system(' '.join(cmd))


def init_config(config_options, iso_dir):
    print("Initializing config...")
    if config_options['KSConfig']:
        os.system('cp ../etc/' + config_options['KSConfig'] + ' ' + iso_dir + '/ks/')


def get_rpm_pubkey(iso_dir):
    print("Getting rpm public key...")
    gpg_tmp = iso_dir + '/GPG_tmp'
    os.system('mkdir -p ' + gpg_tmp)
    os.system('cp ' + iso_dir + '/Packages/openEuler-gpg-keys* ' + gpg_tmp)
    os.system('cd ' + gpg_tmp)
    os.system('rpm2cpio openEuler-gpg-keys* | cpio -div ./etc/pki/rpm-gpg/RPM-GPG-KEY-openEuler')
    os.system('cd -')
    os.system('cp ' + gpg_tmp + '/etc/pki/rpm-gpg/RPM-GPG-KEY-openEuler ' + iso_dir)
    os.system('rm -rf ' + gpg_tmp)


def build_iso(iso_dir):
    os.system('mkdir -p /opt/build-result/')
    cmd = [
        'mkisofs', '-R -J -T -r -l -d',
        '-joliet-long -allow-multidot -allow-leading-dots -no-bak',
        '-V', 'openEuler-21.09-test', '-o', '/opt/build-result/openEuler-21.09-test.iso',
        '-b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4',
        '-boot-info-table  -eltorito-alt-boot -e images/efiboot.img -no-emul-boot',
        iso_dir
    ]


if __name__ == "__main__":
    parsed_args = parser.parse_args()
    with open(parsed_args.config_file, 'r') as config_file:
        config_options = yaml.load(config_file, Loader=yaml.SafeLoader)

    print("Initializing variables...")
    host_arch = os.uname().machine

    pkg_list = parse_package_list(parsed_args.package_list)

    # Check and create working and logging directory
    if not os.path.exists(config_options['WorkingDir']):
        os.makedirs(config_options['WorkingDir'])
    if not os.path.exists(config_options['LogPath']):
        os.makedirs(config_options['LogPath'])

    logger = log_helper.Logger(config_options['LogPath'] + '/ofs.log', logging.ERROR, logging.DEBUG)

    # Cleanup previously built iso file
    iso_dir = config_options['WorkingDir'] + '/iso'
    if os.path.exists(iso_dir):
        os.removedirs(iso_dir)

    # Initializing system configs from config file
    upstream_repo = config_options['UpstreamRepo']
    package_list = config_options['PackageList']

    try:
        release = config_options['ProductRelease']
    except:
        release = ""

#    release_name = "-".join([str(config_options['ProductName']),
#                             str(config_options['ProductVersion']),
#                             release, host_arch])

    run_status = create_install_img(config_options, host_arch, iso_dir)
    create_repos(config_options)
    download_rpms(pkg_list, config_options, iso_dir)
    init_config(config_options, iso_dir)
    get_rpm_pubkey(iso_dir)
    build_iso(iso_dir)

    cleanup(config_options)



