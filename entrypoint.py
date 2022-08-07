import os
import sys
import logging
import gnupg
import shutil
import re
import json
from debian.debfile import DebFile
from key import detectPublicKey, importPrivateKey

debug = os.environ.get('INPUT_DEBUG', False)

if debug:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    logging.info('-- Parsing input --')

    supported_arch = os.environ.get('INPUT_REPO_SUPPORTED_ARCH')
    supported_version = os.environ.get('INPUT_REPO_SUPPORTED_VERSION')
    deb_file_path = os.environ.get('INPUT_FILE')
    deb_file_target_version = os.environ.get('INPUT_FILE_TARGET_VERSION')
    github_repo = os.environ.get('GITHUB_REPOSITORY')

    apt_folder = os.environ.get('INPUT_REPO_FOLDER', 'repo')

    if None in (supported_arch, supported_version, deb_file_path):
        logging.error('Required key is missing')
        sys.exit(1)

    supported_arch_list = supported_arch.strip().split('\n')
    supported_version_list = supported_version.strip().split('\n')
    deb_file_path = deb_file_path.strip()
    deb_file_version = deb_file_target_version.strip()

    logging.debug(supported_arch_list)
    logging.debug(supported_version_list)
    logging.debug(deb_file_path)
    logging.debug(deb_file_version)

    if deb_file_version not in supported_version_list:
        logging.error('File version target is not listed in repo supported version list')
        sys.exit(1)

    key_public = os.environ.get('INPUT_PUBLIC_KEY')
    key_private = os.environ.get('INPUT_PRIVATE_KEY')
    key_passphrase = os.environ.get('INPUT_KEY_PASSPHRASE')

    logging.debug(supported_arch_list)
    logging.debug(supported_version_list)

    logging.info('-- Done parsing input --')

    logging.debug("cwd : {}".format(os.getcwd()))
    logging.debug(os.listdir())

    deb_file_handle = DebFile(filename=deb_file_path)
    deb_file_control = deb_file_handle.debcontrol()

    current_metadata = {
        'format_version': 1,
        'sw_version': deb_file_control['Version'],
        'sw_architecture': deb_file_control['Architecture'],
        'linux_version': deb_file_version
    }

    logging.info('-- Done cloning current Github page --')

    # Prepare repo

    logging.info('-- Preparing repo directory --')

    apt_dir = apt_folder
    apt_conf_dir = os.path.join(apt_dir, 'conf')

    if not os.path.isdir(apt_dir):
        logging.info('Existing repo not detected, creating new repo')
        os.mkdir(apt_dir)
        os.mkdir(apt_conf_dir)
    

    # Prepare key

    logging.info('-- Importing key --')
    key_dir = os.path.join(apt_dir, 'public.key')
    gpg = gnupg.GPG()

    detectPublicKey(gpg, key_dir, key_public)
    private_key_id = importPrivateKey(gpg, key_private)

    logging.info('-- Done importing key --')


    logging.debug('Creating repo config')

    with open(os.path.join(apt_conf_dir, 'distributions'), 'w') as distributions_file:
        for codename in supported_version_list:
            distributions_file.write('Description: {}\n'.format(github_repo))
            distributions_file.write('Codename: {}\n'.format(codename))
            distributions_file.write('Architectures: {}\n'.format(' '.join(supported_arch_list)))
            distributions_file.write('Components: main\n')
            distributions_file.write('SignWith: {}\n'.format(private_key_id))
            distributions_file.write('\n\n')

    logging.info('-- Done preparing repo directory --')

    # Fill repo

    logging.info('-- Adding package to repo --')

    logging.info('Adding {}'.format(deb_file_path))
    os.system(
        'reprepro -b {} --export=silent-never includedeb {} {}'.format(
            apt_dir,
            deb_file_version,
            deb_file_path,
        )
    )

    logging.debug('Signing to unlock key on gpg agent')
    gpg.sign('test', keyid=private_key_id, passphrase=key_passphrase)

    logging.debug('Export and sign repo')
    os.system('reprepro -b {} export'.format(apt_dir))

    logging.info('-- Done adding package to repo --')
