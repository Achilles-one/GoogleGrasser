# coding:utf-8
import json
import os


class ConfigManager(object):
    def __init__(
            self,
            config_file_name: str
    ) -> None:
        self.config_file = f"Config/{config_file_name}.json"

    def return_all_config(self) -> list:
        with open(self.config_file, "r+") as config_file:
            configs = config_file.read()
            config_dict = json.loads(configs)
        return list(config_dict.keys())

    def new_config(
            self,
            language_list: list,
            config_name: str
    ) -> None:
        with open(self.config_file, "r+") as config_file:
            configs = config_file.read()
            config_dict = json.loads(configs)
            if config_name in config_dict:
                config_dict[config_name] = language_list
            else:
                raise NameError("没有此config，请检查输入是否正确。")
            config_file.write(json.dumps(
                config_dict,
                sort_keys=True,
                indent=4, separators=(',', ': '))
            )

    def remove_config(
            self,
            config_name: str
    ) -> None:
        with open(self.config_file, "r+") as config:
            config = config.read()
            config_dict = json.loads(config)
            if config_name in config_dict:
                config_dict.pop(config_name)
            else:
                raise NameError("没有此config，请检查输入是否正确。")

    def return_config(
            self,
            config_name: str
    ) -> list:
        with open(self.config_file, "r+") as config:
            config = config.read()
            config_dict = json.loads(config)
        if config_name in config_dict:
            return config_dict[config_name]
        else:
            raise NameError("没有此config，请检查输入是否正确。")

    def import_config(
            self,
            config_file: str
    ) -> None:
        if os.path.exists(config_file) and os.path.isfile(config_file) and config_file.endswith(".json"):
            with open(config_file, "r+") as config:
                config = config.read()
                config_dict = json.loads(config)
                for key in config_dict:
                    self.new_config(config_dict[key], key)
        else:
            raise FileNotFoundError("没有此json文件。")

    def export_config(
            self,
            config_name_list: list,
            export_config_file_name: str
    ) -> None:
        export_config_file_name = export_config_file_name + ".json"
        with open(f"export_config/{export_config_file_name}", "w+") as export_config_file:
            with open(self.config_file, "r+").read() as config:
                config_dict = json.loads(config)
                export_config_dict = {}
                for v in config_name_list:
                    export_config_dict[v] = config_dict[v]
                export_config_file.write(json.dumps(
                    export_config_dict,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': '))
                )
