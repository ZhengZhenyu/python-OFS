import glob
import os

import patch
from pyrpm.spec import Spec, replace_macros


def handling_patches(package_list, work_dir, logger):
    for package in package_list:
        for k in package.keys():
            package_name = k

        dest_dir = work_dir + '/' + package_name
        spec_file = glob.glob(dest_dir + '/' + '*.spec')[0]
        logger.debug("[Patcher] Parsing spec file: " + spec_file)
        spec = Spec.from_file(spec_file)
        # Using workaround method as some of the versions in spec does not
        # reflect source code package version
        # spec.version = replace_macros(spec.version, spec)
        tar_name = glob.glob(dest_dir + '/' + package_name + '*.tar.*')[0]
        folder_name = tar_name.split('.tar')[0]

        prevdir = os.getcwd()
        os.chdir(dest_dir)

        patch_count = 1
        if spec.patches:
            for i in range(len(spec.patches)):
                spec.patches[i] = replace_macros(spec.patches[i], spec)
            for patch_name in spec.patches:
                logger.debug("[Patcher] Patching patch#" + str(patch_count) + ": " + patch_name)
                pset = patch.fromfile(patch_name)
                # Using workaround method as some of the versions in spec does not
                # reflect source code package version
                # spec.version = replace_macros(spec.version, spec)
                # pset.apply(root=dest_dir + '/' + package_name + '-' + spec.version)
                if not pset:
                    logger.debug("[Patcher] Patch#" + str(patch_count) + ": " + patch_name + " failed...")
                else:
                    pset.apply(root=folder_name)
                patch_count += 1

        os.chdir(prevdir)
