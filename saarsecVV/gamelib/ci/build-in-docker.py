import os
import shutil
import subprocess
import sys
from typing import Dict

import yaml


# USAGE:
# ./build-in-docker.py
# ./build-in-docker.py --sudo   (if your docker setup requires root)


def docker_image_exists(image_name: str) -> bool:
    output = subprocess.check_output(['docker', 'images', '-q', image_name])
    return len(output) >= 12


def build_ci_base_image(image: str):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docker-saarctf-ci-base')
    script = [os.path.join(path, 'docker-build.sh')]
    print(f'[-] Image {image} is not present, building ...')
    if '--sudo' in sys.argv:
        script = ['sudo'] + script
    subprocess.check_call(script, cwd=path)
    print(f'[*] Image {image} has been created.')


def build():
    basefolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output = os.path.join(basefolder, 'build_output')
    with open(os.path.join(basefolder, '.gitlab-ci.yml'), 'r') as f:
        ci_config: Dict = yaml.safe_load(f)
    image = ci_config.get('build', {}).get('image', 'saarsec/saarctf-ci-base:latest')
    # Create output folder
    if os.path.exists(output):
        shutil.rmtree(output)
    os.makedirs(output)
    if image.startswith('saarsec/saarctf-ci-base'):
        if not docker_image_exists(image):
            build_ci_base_image(image)
    try:
        # Invoke Docker
        build_cmd = ' && '.join([
            'cp -r /opt/input/*.sh /opt/input/service /opt/input/servicename /opt/output/',
            '(timeout 3 /opt/input/gamelib/ci/buildscripts/test-and-configure-aptcache.sh || echo "no apt cache found. Install apt-cacher-ng for better performance!")',
            'cd /opt/output',
            './build.sh',
            f'chown -R {os.getuid()} .'
        ])
        cmd = ['docker', 'run', '-v', f'{basefolder}:/opt/input:ro', '-v', f'{output}:/opt/output:rw']
        cmd += ['--rm']
        cmd += [image]
        cmd += ['/bin/sh', '-c', build_cmd]
        if '--sudo' in sys.argv:
            cmd = ['sudo'] + cmd
        print(f'[-] Invoking docker to build ...')
        print('>', ' '.join(cmd))
        subprocess.check_call(cmd)
        print(f'[*] Service has been built and written to "{output}".')
    except:
        shutil.rmtree(output)
        raise


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build-ci-base':
        image = 'saarsec/saarctf-ci-base:latest'
        if not docker_image_exists(image):
            build_ci_base_image(image)
    else:
        build()
