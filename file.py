import logging
import yaml
from exceptions import FileValidateError


class File:
    def __init__(self, filepath):
        self.__filepath = filepath
        self.__docker_block_name = 'dockerImages'
        self.__helm_block_name = 'helmCharts'

        with open(self.__filepath, "r") as file:
            self.__yaml_data = yaml.safe_load(file)

    def output_data(self):
        return self.__yaml_data

    def check_artifact_block(self, artifact_block_name):
        if artifact_block_name in self.__yaml_data.keys():
            return True
        else:
            return False

    def check_docker_keys(self):
        for artifact in self.__yaml_data[self.__docker_block_name]:
            if not (('tags' in artifact.keys()) and ('name' in artifact.keys())):
                logging.error(f'Check if keys for docker image are correct: {artifact}')
                return False
        return True

    def check_helm_keys(self):
        for artifact in self.__yaml_data[self.__helm_block_name]:
            if not (('tags' in artifact.keys()) and ('name' in artifact.keys()) and ('repo' in artifact.keys())):
                logging.error(f'Check if keys for helm chart are correct: {artifact}')
                return False
        return True

    def check_docker_tags_values_type(self):
        for artifact in self.__yaml_data[self.__docker_block_name]:
            if not type(artifact['tags']) is list:
                logging.error(f'The tags key must contain a list for image {artifact}')
                return False
        return True

    def check_helm_tags_values_type(self):
        for artifact in self.__yaml_data[self.__helm_block_name]:
            if not type(artifact['tags']) is list:
                logging.error(f'The tags key must contain a list for chart {artifact}')
                return False
        return True

    def validate_docker_block(self):
        if not self.check_artifact_block(self.__docker_block_name):
            raise FileValidateError(f'Unable to detect block listing Docker images')
        if not self.check_docker_keys():
            raise FileValidateError(f'Key validation problem')
        if not self.check_docker_tags_values_type():
            raise FileValidateError(f'Key value validation problem')
        return True

    def validate_helm_block(self):
        if not self.check_artifact_block(self.__helm_block_name):
            raise FileValidateError(f'Unable to detect block listing Helm charts')
        if not self.check_helm_keys():
            raise FileValidateError(f'Key validation problem')
        if not self.check_helm_tags_values_type():
            raise FileValidateError(f'Key value validation problem')
        return True

    def get_docker_images_list(self):
        return self.__yaml_data[self.__docker_block_name]

    def get_helm_charts_list(self):
        return self.__yaml_data[self.__helm_block_name]
