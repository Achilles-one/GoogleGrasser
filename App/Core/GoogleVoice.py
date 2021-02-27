import requests
from googletrans.gtoken import TokenAcquirer
from pydub import AudioSegment


class GoogleVoice(object):

    def __init__(
            self,
            service_url: str = "translate.google.cn"
    ):
        from constants import SERVICE_URLS
        if service_url in SERVICE_URLS:
            self.service_url = service_url
        else:
            self.service_url = "translate.google.cn"
        self.token_tool = TokenAcquirer(None, host=self.service_url)

    @staticmethod
    def splicing_audio(
            file_list: list,
            output_file
    ) -> None:
        try:
            output_music = AudioSegment.empty()
            for i in file_list:
                output_music += AudioSegment.from_file(i, "mp3")
            output_music += AudioSegment.silent(duration=1000)
            output_music.export(output_file, format="mp3")
        except BaseException as Error:
            raise Error

    def get_token(
            self,
            text: str
    ) -> str:
        return self.token_tool.do(text)

    def output_voice(
            self,
            text: str,
            output_file: str = "Output.mp3",
            language: str = "zh-cn"
    ) -> None:
        output_file = f"Output/{output_file}"
        try:
            string_after_modification = text.replace("%20", " ")
            url = "https://{}/translate_tts?ie=UTF-8&q={}&tl={}&total=1&idx=0&textlen={}&tk={}&client=webapp".format(
                self.service_url,
                string_after_modification,
                language,
                str(len(text)),
                self.get_token(text)
            )
            context = requests.get(url, timeout=3000)
            with open(output_file, "wb") as output_file:
                for data in context.iter_content(chunk_size=1024):
                    if data:
                        output_file.write(data)
        except ConnectionError:
            raise ConnectionError("请求失败")
