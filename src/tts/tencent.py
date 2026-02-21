import wave
import time
from .common import credential
from . import flowing_speech_synthesizer
from .common.log import logger
from .common.utils import is_python3
import os
import dotenv
from typing import List, TypedDict, Optional

dotenv.load_dotenv()

APPID = os.environ.get("TENCENT_APP_ID")
SECRET_ID = os.environ.get("TENCENT_SECRET_ID")
SECRET_KEY = os.environ.get("TENCENT_SECRET_KEY")


class VoiceType(TypedDict):
    VOICETYPE: int
    CODEC: str
    SAMPLE_RATE: int
    ENABLE_SUBTITLE: bool


class MySpeechSynthesisListener(
    flowing_speech_synthesizer.FlowingSpeechSynthesisListener
):

    def __init__(self, codec, sample_rate, id=None):
        self.start_time = time.time()
        self.id = id
        self.codec = codec.lower()
        self.sample_rate = sample_rate

        self.audio_file = ""
        self.audio_data = bytes()

    def set_audio_file(self, filename):
        self.audio_file = filename

    def on_synthesis_start(self, session_id):
        """
        session_id: 请求session id，类型字符串
        """
        if is_python3():
            super().on_synthesis_start(session_id)
        else:
            super(MySpeechSynthesisListener, self).on_synthesis_start(session_id)

        # TODO 合成开始，添加业务逻辑
        if not self.audio_file:
            self.audio_file = "speech_synthesis_output." + self.codec
        self.audio_data = bytes()

    def on_synthesis_end(self):
        if is_python3():
            super().on_synthesis_end()
        else:
            super(MySpeechSynthesisListener, self).on_synthesis_end()

        # TODO 合成结束，添加业务逻辑
        logger.info(
            "write audio file, path={}, size={}".format(
                self.audio_file, len(self.audio_data)
            )
        )
        if self.codec == "pcm":
            wav_fp = wave.open(self.audio_file + ".wav", "wb")
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(2)
            wav_fp.setframerate(self.sample_rate)
            wav_fp.writeframes(self.audio_data)
            wav_fp.close()
        elif self.codec == "mp3":
            fp = open(self.audio_file + ".mp3", "wb")
            fp.write(self.audio_data)
            fp.close()
        else:
            logger.info(
                "codec {}: sdk NOT implemented, please save the file yourself".format(
                    self.codec
                )
            )

    def on_audio_result(self, audio_bytes):
        """
        audio_bytes: 二进制音频，类型 bytes
        """
        if is_python3():
            super().on_audio_result(audio_bytes)
        else:
            super(MySpeechSynthesisListener, self).on_audio_result(audio_bytes)

        # TODO 接收到二进制音频数据，添加实时播放或保存逻辑
        self.audio_data += audio_bytes

    def on_text_result(self, response):
        """
        response: 文本结果，类型 dict，如下
        字段名       类型         说明
        code        int         错误码（无需处理，FlowingSpeechSynthesizer中已解析，错误消息路由至 on_synthesis_fail）
        message     string      错误信息
        session_id  string      回显客户端传入的 session id
        request_id  string      请求 id，区分不同合成请求，一次 websocket 通信中，该字段相同
        message_id  string      消息 id，区分不同 websocket 消息
        final       bool        合成是否完成（无需处理，FlowingSpeechSynthesizer中已解析）
        result      Result      文本结果结构体

        Result 结构体
        字段名       类型                说明
        subtitles   array of Subtitle  时间戳数组

        Subtitle 结构体
        字段名       类型     说明
        Text        string  合成文本
        BeginTime   int     开始时间戳
        EndTime     int     结束时间戳
        BeginIndex  int     开始索引
        EndIndex    int     结束索引
        Phoneme     string  音素
        """
        if is_python3():
            super().on_text_result(response)
        else:
            super(MySpeechSynthesisListener, self).on_text_result(response)

        # TODO 接收到文本数据，添加业务逻辑
        result = response["result"]
        subtitles = []
        if "subtitles" in result and len(result["subtitles"]) > 0:
            subtitles = result["subtitles"]

    def on_synthesis_fail(self, response):
        """
        response: 文本结果，类型 dict，如下
        字段名 类型
        code        int         错误码
        message     string      错误信息
        """
        if is_python3():
            super().on_synthesis_fail(response)
        else:
            super(MySpeechSynthesisListener, self).on_synthesis_fail(response)

        # TODO 合成失败，添加错误处理逻辑
        err_code = response["code"]
        err_msg = response["message"]


def process(
    texts: list, output_dir: str, output_file_prefix: str, voice_type: VoiceType
):
    listener = MySpeechSynthesisListener(voice_type["CODEC"], voice_type["SAMPLE_RATE"])
    os.makedirs(output_dir, exist_ok=True)
    listener.set_audio_file(os.path.join(output_dir, output_file_prefix))

    credential_var = credential.Credential(SECRET_ID, SECRET_KEY)
    synthesizer = flowing_speech_synthesizer.FlowingSpeechSynthesizer(
        APPID, credential_var, listener
    )
    synthesizer.set_voice_type(voice_type["VOICETYPE"])
    synthesizer.set_codec(voice_type["CODEC"])
    synthesizer.set_sample_rate(voice_type["SAMPLE_RATE"])
    synthesizer.set_enable_subtitle(voice_type["ENABLE_SUBTITLE"])

    synthesizer.start()
    ready = synthesizer.wait_ready(5000)
    if not ready:
        logger.error("wait ready timeout")
        return

    while True:
        for text in texts:
            synthesizer.process(text)
            time.sleep(5)  # 模拟文本流式生成
        break
    synthesizer.complete()  # 发送合成完毕指令

    synthesizer.wait()  # 等待服务侧合成完成

    logger.info("process done")
