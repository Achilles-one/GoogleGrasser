from UI_GoogleGrasser import Ui_application

from PySide6.QtWidgets import *
from PySide6.QtCore import *

from Grasser import GoogleGrasser
from ConfigManager import ConfigManager
from SettingsManager import SettingsManager
from GoogleVoice import GoogleVoice
import Grasser
import constants

import langid
import os
import pyperclip


class OnClick(QObject):
    set_grass_result = Signal(Grasser.GrassResult, name="GrassResult")
    warning = Signal(str, str, name="Warning")
    quit = Signal(name="exit")

    def __init__(
            self,
            parent
    ):
        super(OnClick, self).__init__(parent)
        self.google_voice = GoogleVoice()

    def output_grass_voice(
            self,
            output_file: str,
    ) -> None:
        if "grass_result" in vars(self):
            grass_string = self.grass_result.text
            try:
                if len(grass_string) <= 198:
                    self.google_voice.output_voice(grass_string, output_file)
                else:
                    number = len(grass_string) // 198
                    number_of_remaining_digits = len(grass_string) % 198
                    for i in range(number):
                        __CacheString__ = grass_string[i * 198:(i + 1) * 198]
                        self.google_voice.output_voice(
                            "__Cache__/__Cache__{}.mp3".format(i + 1),
                            __CacheString__
                        )
                    self.google_voice.output_voice(
                        grass_string[number * 198:number * 198 + number_of_remaining_digits],
                        "__Cache__/__Cache__{}.mp3".format(number + 1)
                    )
                    input_list = []
                    for a, b, c in os.walk(r'__Cache__/'):
                        for i in c:
                            input_list.append("__Cache__/{}".format(i))
                    self.google_voice.splicing_audio(input_list, output_file)
                    for i in input_list:
                        os.remove(i)
            except FileExistsError:
                self.warning.emit("请勿删除__Cache__文件夹或内部的任意文件")
        else:
            self.warning.emit("错误", "没有生草结果，无法保存文件")
            self.quit.emit()

    def on_start_grass_click(
            self,
            grasser: Grasser.GoogleGrasser,
            original_text: str,
            grass_frequency: int,
            config_name: str,
    ) -> None:
        if original_text == "":
            self.warning.emit("错误", "输入不能为空")
        elif langid.classify(original_text)[0] != "zh":
            self.warning.emit("错误", "需要生草的语言必须为中文")
        else:
            if config_name == "随机":
                grass_result = grasser.get_random_grass(
                    original_text, grass_frequency
                )
            else:
                grass_result = grasser.get_config_grass(
                    original_text,
                    config_name,
                    grass_frequency
                )
            self.set_grass_result.emit(grass_result)
        self.quit.emit()

    def on_output_google_voice_click(
            self,
            output_file: str
    ) -> None:
        self.output_grass_voice(output_file)
        self.quit.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.grass_result: Grasser.GrassResult
        self.settings_manager = SettingsManager()
        self.settings_manager.setup_settings(self)
        self.grasser = GoogleGrasser(
            config_file_name=self.config_file_name,
            service_url=self.google_translate_service_url,
            no_english=self.random_grass_no_english
        )
        self.config_manager = ConfigManager(
            self.config_file_name
        )

        self.change_style(self.application_style)

        self.ui = Ui_application()
        self.ui.setupUi(self)
        self.ui.select_config.addItems(
            ["随机"] + self.config_manager.return_all_config()
        )
        self.ui.select_google_translate_url.addItems(constants.SERVICE_URLS)
        self.ui.select_application_style.addItems(QStyleFactory.keys())

        self.GrassingThread = QThread(self)
        self.OnClick = OnClick(self)
        self.OnClick.moveToThread(self.GrassingThread)

        self.ui.start_grass.clicked.connect(self.on_start_grass_click)
        self.ui.open_file.clicked.connect(self.on_open_file_click)
        self.ui.copy_result.clicked.connect(self.on_copy_result_click)
        self.ui.save_this_grass_as_config.clicked.connect(self.on_save_this_grass_as_config_click)
        self.ui.save_result.clicked.connect(self.on_save_grass_result_click)

        self.OnClick.set_grass_result.connect(self.set_grass_result)
        self.OnClick.warning.connect(self.warning_dialog)
        self.OnClick.quit.connect(self.quit_onclick_thread)
        self.ui.select_google_translate_url.currentTextChanged.connect(
            self.on_select_google_translate_url_current_index_changed
        )
        self.GrassingThread.started.connect(
            lambda:
            self.OnClick.on_start_grass_click(
                self.grasser,
                self.ui.original_text_edit.toPlainText(),
                self.ui.grass_frequency.value(),
                self.ui.select_config.currentText()
            )
        )
        self.ui.second_setting_option_button_group.buttonClicked.connect(
            self.on_second_setting_option_click
        )
        self.ui.set_config_file_name.returnPressed.connect(
            self.on_set_config_file_name_return_pressed
        )
        self.ui.select_application_style.currentTextChanged.connect(
            self.select_application_style_current_index_changed
        )

        self.ui.select_google_translate_url.setCurrentIndex(
            constants.SERVICE_URLS.index(self.google_translate_service_url)
        )
        self.ui.select_application_style.setCurrentIndex(
            QStyleFactory.keys().index(self.application_style)
        )

        if self.random_grass_no_english:
            self.ui.radio_first_setting_option.setChecked(True)
        else:
            self.ui.radio_second_setting_option.setChecked(True)

    def on_start_grass_click(self) -> None:
        self.GrassingThread.start()

    def on_open_file_click(self) -> None:
        file_name = QFileDialog.getOpenFileName(self, "选择要生草的txt文件", "", "Txt files(*.txt)")
        if file_name[0] != "":
            with open(file_name[0], "r+", encoding="utf-8") as file:
                text = file.read()
            self.ui.original_text_edit.setPlainText(text)

    def on_copy_result_click(self) -> None:
        pyperclip.copy(self.grass_result.text)

    def on_save_this_grass_as_config_click(self) -> None:
        if "grass_result" in vars(self):
            config_name, ok_pressed = QInputDialog.getText(
                self,
                "输入配置名称",
                "名称:",
                QLineEdit.Normal,
                "")
            if ok_pressed:
                self.config_manager.new_config(self.grass_result.language_list, config_name)
        else:
            self.warning_dialog("错误", "没有生草结果，无法生成配置")

    def on_save_grass_result_click(self) -> None:
        if "grass_result" in vars(self):
            file_path, ok_pressed = QFileDialog.getSaveFileName(
                self,
                "保存生草结果文件",
                "",
                "txt类型 (*.txt)"
            )
            if ok_pressed:
                with open(file_path, "w+") as output_file:
                    output_file.write(self.grass_result.text)
        else:
            self.warning_dialog("错误", "没有生草结果，无法保存文件")

    def on_output_google_voice_click(self) -> None:
        file_name, ok_pressed = QInputDialog.getText(self, "请输入文件名", "文件名", QLineEdit.Normal)
        if ok_pressed:
            self.GrassingThread.started.connect(
                lambda:
                self.OnClick.on_output_google_voice_click(
                    file_name
                )
            )

    def on_select_google_translate_url_current_index_changed(self) -> None:
        service_url = self.ui.select_google_translate_url.currentText()
        self.settings_manager.manage_setting("google_translate_service_url", service_url)

    def on_second_setting_option_click(self) -> None:
        self.settings_manager.manage_setting(
            "random_grass_no_english",
            True if self.ui.second_setting_option_button_group.checkedButton().text() == "是" else False
        )

    def on_set_config_file_name_return_pressed(self) -> None:
        self.settings_manager.manage_setting("config_file_name", self.ui.set_config_file_name.text())

    def select_application_style_current_index_changed(self):
        self.settings_manager.manage_setting("application_style", self.ui.select_application_style.currentText())

    def set_grass_result(
            self,
            grass_result: Grasser.GrassResult
    ) -> None:
        self.ui.grass_result_browser.setText(grass_result.text)
        vars(self)["grass_result"] = grass_result

    def quit_onclick_thread(self) -> None:
        self.GrassingThread.quit()

    def warning_dialog(
            self,
            title: str,
            content_text: str
    ) -> None:
        QMessageBox(QMessageBox.Warning, title, content_text, parent=self).exec_()

    @staticmethod
    def change_style(
            style_name: str
    ) -> None:
        styles = QStyleFactory.keys()
        if style_name not in styles:
            QApplication.setStyle(styles[0])
            raise NameError("没有此主题，使用默认主题")
        else:
            QApplication.setStyle(style_name)


if __name__ == '__main__':
    application = QApplication()
    main_window = MainWindow()
    main_window.show()
    application.exec_()
