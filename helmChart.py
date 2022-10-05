import logging
from utils import exec_command


class HelmChart:
    def __init__(self, chart_name, chart_version, chart_public_registry):
        self.__name = chart_name
        self.__version = chart_version
        self.__public_registry = chart_public_registry
        self.__local_repo_name = 'tmp'

    def get_name_with_version(self) -> str:
        return f'{self.__name}-{self.__version}'

    def add_repo(self, public_repo) -> bool:
        command = f'helm repo add {self.__local_repo_name} https://{public_repo}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def pull(self) -> bool:
        command = f'helm pull {self.__local_repo_name}/{self.__name} --version {self.__version}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def save_chart(self, public_repo):
        if not self.add_repo(public_repo):
            raise RuntimeError(f'Failed to add repository for {self.__name}:{self.__version} chart')
        if not self.pull():
            raise RuntimeError(f'Failed to pull {self.__name}:{self.__version} chart')
        if not self.delete_repo():
            raise RuntimeError(f'Failed to clear local repo')
        print(f'{self.__name}-{self.__version}  helm chart save successfully')
        return True

    def delete_repo(self) -> bool:
        command = f'helm repo remove {self.__local_repo_name}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def push_to_nexus(self, url, login, password) -> bool:
        command = f'curl -u {login}:{password} https://{url} --upload-file {self.__name}-{self.__version}.tgz -v'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def delete_local_chart(self):
        command = f'rm {self.__name}-{self.__version}.tgz'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def nexus_migrate(self, public_repo, registry_url, registry_login, registry_password):
        if not self.add_repo(public_repo):
            raise RuntimeError(f'Failed to add repository for {self.__name}-{self.__version} chart')
        if not self.pull():
            raise RuntimeError(f'Failed to pull {self.__name}-{self.__version} chart')
        if not self.delete_repo():
            raise RuntimeError(f'Failed to clear local repo')
        if not self.push_to_nexus(registry_url, registry_login, registry_password):
            raise RuntimeError(f'Failed to push {self.__name}-{self.__version} chart in nexus registry')
        if not self.delete_local_chart():
            raise RuntimeError(f'Failed delete chart {self.__name}-{self.__version}.tgz')
        print(f'{self.__name}-{self.__version}  helm chart migrated successfully')
