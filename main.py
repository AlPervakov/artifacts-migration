import argparse
import logging
import sys

from file import File
from dockerImage import DockerImage
from helmChart import HelmChart
from utils import exec_command
from exceptions import FileValidateError, ExecCommandError
from loguru import logger


def parse_args():
    parser = argparse.ArgumentParser(
        description='The script allows you to\
       download helm charts and docker images from public repositories\
       and upload them to the internal repository')

    parser.add_argument('file', type=str, help='YAML file with Docker images and Helm charts list')
    parser.add_argument('-m', '--mode', dest='mode', type=str, choices=['save', 'migrate'], required=True, help='mode')
    parser.add_argument('-u', dest='registry_login', type=str, help='Login for internal registry')
    parser.add_argument('-p', dest='registry_password', type=str, help='Password for internal registry')
    parser.add_argument('-dr', dest='docker_registry_url', type=str, help='Internal Docker registry')
    parser.add_argument('-hr', dest='helm_registry_url', type=str, help='Internal Helm registry')
    parser.add_argument('-l', '--log-level', dest='log_level', type=str, help='Log level', default='INFO')

    return parser.parse_args()


def init_logging(logging_level):
    numeric_level = getattr(logging, logging_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logging_level)
    logging.basicConfig(format='%(asctime)s %(message)s', level=numeric_level)


def docker_login(docker_internal_registry_url, registry_login, registry_password):
    command = f'docker login {docker_internal_registry_url} -u {registry_login} -p {registry_password}'
    stdout, stderr, result = exec_command(command)
    logging.debug(stdout)
    logging.error(stderr)
    return result


def docker_logout():
    command = f'docker logout'
    stdout, stderr, result = exec_command(command)
    logging.debug(stdout)
    logging.error(stderr)
    return result


def check_utils(util):
    command = f'{util}'
    stdout, stderr, result = exec_command(command)
    logging.debug(stdout)
    logging.debug(stderr)
    if not result:
        raise ExecCommandError(f'{stderr}')


def handle_docker() -> list:
    problem_list = []
    if args.mode == 'migrate':
        if not docker_login(args.docker_registry_url, args.registry_login, args.registry_password):
            problem_list.append('Docker: Failed to login')
            raise ExecCommandError('Docker: Failed to login')
    for image in data.get_docker_images_list():
        for tag in image['tags']:
            artifact = DockerImage(image['name'], str(tag))
            try:
                if args.mode == 'migrate':
                    # print(f'Image MIGRATE {str(tag)}')  # Test
                    artifact.migrate(args.docker_registry_url)
                if args.mode == 'save':
                    # print(f'Image SAVE {str(tag)}')  # Test
                    artifact.pull()
            except RuntimeError as e:
                logging.error(e)
                problem_list.append(artifact.get_name_with_tag())
    if args.mode == 'migrate':
        docker_logout()
    return problem_list


def handle_helm() -> list:
    problem_list = []
    for chart in data.get_helm_charts_list():
        for tag in chart['tags']:
            artifact = HelmChart(chart['name'], str(tag), chart['repo'])
            try:
                if args.mode == 'migrate':
                    # print(f'Chart MIGRATE {str(tag)}')  # Test
                    artifact.nexus_migrate(chart['repo'], args.helm_registry_url, args.registry_login,
                                           args.registry_password)
                if args.mode == 'save':
                    # print(f'Chart SAVE {str(tag)}')  # Test
                    artifact.save_chart(chart['repo'])
            except RuntimeError as e:
                logging.error(e)
                problem_list.append(artifact.get_name_with_version())
    return problem_list


def main():
    is_error_artifact_migrate = False
    docker_problems = []
    helm_problems = []

    try:
        if data.validate_docker_block():
            check_utils('docker version')
            docker_problems = handle_docker()
    except FileValidateError as e:
        is_error_artifact_migrate = True
        logging.error(e)
    except ExecCommandError as e:
        is_error_artifact_migrate = True
        logging.error(e)

    try:
        if data.validate_helm_block():
            check_utils('helm version')
            helm_problems = handle_helm()
    except FileValidateError as e:
        is_error_artifact_migrate = True
        logging.error(e)

    if len(docker_problems) != 0 or len(helm_problems) != 0:
        is_error_artifact_migrate = True

    return is_error_artifact_migrate


if __name__ == '__main__':
    args = parse_args()
    data = File(args.file)
    init_logging(args.log_level)
    # logger.add(sys.stdout, format="{time} {level} {message}", filter="my_module", level="INFO")
    if main():
        exit(1)
