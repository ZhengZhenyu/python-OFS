import glob
import tarfile

import git as pg


def clone_and_checkout(package_list, target_release, work_dir, logger):

    for package in package_list:
        for k, v in package.items():
            package_name = k
            package_url = v

        dest_dir = work_dir + '/' + package_name
        logger.debug("[Downloader] Cloning " + package_name + " to dir: " +
                     dest_dir + " and checkout to: " + target_release)

        try:
            cloned = git_clone_and_checkout(
                source_url=package_url,
                dest_dir=dest_dir,
                aimed_branch=target_release)
        except Exception:
            logger.debug("[Downloader] Repo exist, skipping ...")


def git_clone_and_checkout(source_url, dest_dir, aimed_branch='main'):
    cloned_repo = pg.repo.Repo.clone_from(url=source_url, to_path=dest_dir)
    git_obj = cloned_repo.git
    git_obj.checkout(aimed_branch)
    return cloned_repo


def tar_extract(package_list, work_dir, logger):
    for package in package_list:
        for k in package.keys():
            package_name = k

        dest_dir = work_dir + '/' + package_name
        tar_names = glob.glob(dest_dir + '/' + package_name + '*.tar.*')
        if tar_names:
            for tar_name in tar_names:
                logger.debug("[Downloader] Extracting " + tar_name + " ...")
                with tarfile.open(tar_name) as f:
                    f.extractall(dest_dir)
