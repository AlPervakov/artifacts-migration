import logging
import re
from utils import exec_command


class DockerImage:
    def __init__(self, image_name, image_tag):
        self.__name = image_name
        self.__tag = image_tag
        self.__new_image_name = None

    def get_name_with_tag(self) -> str:
        return f'{self.__name}:{self.__tag}'

    def pull(self) -> bool:
        command = f'docker pull {self.__name}:{self.__tag}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def retag(self, registry_path) -> bool:
        inspect_string = re.sub(r'/.*', '', self.__name)
        if re.search(r'[.]', inspect_string):
            clear_image_name = re.sub(inspect_string + '/', '', self.__name)
        else:
            clear_image_name = self.__name
        self.__new_image_name = f'{registry_path}/{clear_image_name}:{self.__tag}'
        command = f'docker image tag {self.__name}:{self.__tag} {self.__new_image_name}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def push(self) -> bool:
        command = f'docker push {self.__new_image_name}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def delete_local_images(self) -> bool:
        command = f'docker rmi {self.__name}:{self.__tag} {self.__new_image_name}'
        stdout, stderr, result = exec_command(command)
        logging.debug(stdout)
        logging.debug(stderr)
        return result

    def migrate(self, registry_url):
        if not self.pull():
            raise RuntimeError(f'{self.__name}:{self.__tag} image pull error')
        if not self.retag(registry_url):
            raise RuntimeError(f'{self.__name}:{self.__tag} image retag error')
        if not self.push():
            raise RuntimeError(f'{self.__name}:{self.__tag} image push error')
        if not self.delete_local_images():
            logging.error(f'Failed to clear local images: {self.__name}:{self.__tag} and {self.__new_image_name}.')
        print(f'{self.__name}:{self.__tag} image migrated successfully')
