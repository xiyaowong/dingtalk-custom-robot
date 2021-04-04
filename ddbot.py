import base64
import hashlib
import hmac
import logging
import time
import traceback
import urllib.parse
import warnings
from collections.abc import Sequence
from typing import List, Tuple, Union

import httpx

warnings.filterwarnings("ignore")

default_logger = logging.getLogger("ddbot")


class DDBot:
    """钉钉自定义机器人对象(同步)
    :param access_token: 机器人webhook的access_token字段
    :param secret: 机器人的secret字段
    :param logger: 设置为 ``True`` 开启日志或者传入一个 logger 对象用来输出日志,
                    设置为 `False` 来关闭日志，默认为 `True`
    :param timeout: 发起http请求时，允许等待响应的时间
    """

    def __init__(self, access_token: str, secret: str, logger=True, timeout=20):
        self.access_token = access_token
        self.secret = secret
        self.client = httpx.Client(timeout=timeout)

        if not isinstance(logger, bool):
            self.logger = logger
        else:
            self.logger = default_logger
            if not logging.root.handlers and self.logger.level == logging.NOTSET:
                if logger:
                    self.logger.setLevel(logging.INFO)
                else:
                    self.logger.setLevel(logging.ERROR)
                h = logging.StreamHandler()
                h.setFormatter(
                    logging.Formatter("%(asctime)s[%(levelname)s] %(message)s")
                )
                self.logger.addHandler(h)

    @property
    def webhook(self) -> str:
        """返回完整的webhook地址"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return httpx.URL(
            "https://oapi.dingtalk.com/robot/send",
            {
                "timestamp": timestamp,
                "sign": sign,
                "access_token": self.access_token,
            },
        )

    def post(self, payload: dict) -> Union[dict, str]:
        """发送POST请求
        :param payload: 需要上报的数据(JSON格式)
        :return: 返回响应数据JSON解码后的字典，如果解码失败返回响应的文本内容,
                 如果请求出错，返回None
        """
        try:
            resp = self.client.post(self.webhook, json=payload)
            resp.raise_for_status()
        except Exception:
            self.logger.error(traceback.format_exc())
        else:
            try:
                res = resp.json()
            except Exception:
                self.logger.error("请求返回格式错误")
                res = resp.text
            else:
                if res["errcode"] == 0:
                    self.logger.info(
                        "请求成功 errcode: {errcode}, errmsg: {errmsg}".format(**res)
                    )
                elif res["errcode"] == 310000:
                    self.logger.error(
                        "校验未通过 errcode: {errcode}, errmsg: {errmsg}".format(**res)
                    )
                else:
                    self.logger.error(
                        "API错误 errcode: {errcode}, errmsg: {errmsg}".format(**res)
                    )
            return res
        return None

    def text(
        self, content: str, atMobiles: Union[int, List[int]] = None, isAtAll=False
    ):
        """发送文本(text)类型信息
        :param content: 消息内容
        :param atMobiles: 被@人的手机号，可以是单个手机号或手机号列表
        :param isAtAll: 是否@所有人
        """
        if atMobiles is None:
            atMobiles = []
        elif isinstance(atMobiles, Sequence):
            atMobiles = list(atMobiles)
        else:
            atMobiles = [atMobiles]
        return self.post(
            {
                "msgtype": "text",
                "text": {"content": content},
                "at": {"atMobiles": [str(i) for i in atMobiles], "isAtAll": isAtAll},
            }
        )

    def link(self, title: str, text: str, messageURL: str, picURL: str = ""):
        """发送链接(link)类型消息
        :param title: 消息标题
        :param text: 消息内容
        :param messageURL: 点击消息跳转的URL
        :param picURL: 图片URL
        """
        return self.post(
            {
                "msgtype": "link",
                "link": {
                    "text": text,
                    "title": title,
                    "picUrl": picURL,
                    "messageUrl": messageURL,
                },
            }
        )

    def markdown(
        self,
        title: str,
        text: str,
        atMobiles: Union[int, List[int]] = None,
        isAtAll=False,
    ):
        """发送Markdown类型消息
        :param title: 首屏会话透出的展示内容。
        :param text: markdown格式的消息。
        :param atMobiles: 被@人的手机号，可以是单个手机号或手机号列表
        :param isAtAll: 是否@所有人
        """
        if atMobiles is None:
            atMobiles = []
        elif isinstance(atMobiles, Sequence):
            atMobiles = list(atMobiles)
        else:
            atMobiles = [atMobiles]
        return self.post(
            {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": text},
                "at": {"atMobiles": [str(i) for i in atMobiles], "isAtAll": isAtAll},
            }
        )

    def wholeActionCard(
        self, title: str, text: str, singleTitle: str, singleURL: str, btnOrientation=0
    ):
        """发送整体跳转ActionCard类型消息
        :param title: 首屏会话透出的展示内容。
        :param text: markdown格式的消息。
        :param singleTitle: 单个按钮的标题
        :param singleURL: 点击singleTitle按钮触发的URL。
        :param btnOrientation: 0：按钮竖直排列 1：按钮横向排列
        """
        return self.post(
            {
                "actionCard": {
                    "title": title,
                    "text": text,
                    "btnOrientation": btnOrientation,
                    "singleTitle": singleTitle,
                    "singleURL": singleURL,
                },
                "msgtype": "actionCard",
            }
        )

    def separatedActionCard(
        self,
        title: str,
        text: str,
        btns: Union[Tuple[str, str], List[Tuple[str, str]]],
        btnOrientation=0,
    ):
        """发送独立跳转ActionCard类型消息
        :param title: 首屏会话透出的展示内容。
        :param text: markdown格式的消息。
        :param btns: 按钮。一个元组或多个元组列表，每个元组含有2个元素
                     第1个元素为按钮标题、第2个元素为点击按钮触发的URL。
        :param btnOrientation: 0：按钮竖直排列 1：按钮横向排列
        """
        if isinstance(btns, tuple):
            btns = [btns]
        return self.post(
            {
                "msgtype": "actionCard",
                "actionCard": {
                    "title": title,
                    "text": text,
                    "hideAvatar": "0",
                    "btnOrientation": btnOrientation,
                    "btns": [{"title": i[0], "actionURL": i[1]} for i in btns],
                },
            }
        )

    def feedCard(self, links: Union[Tuple[str, str, str], List[Tuple[str, str, str]]]):
        """发送FeedCard类型消息
        :param links: 信息。一个元组或多个元组列表，每个元组含有3个元素
                    第1个元素为单条信息文本、第2个元素为点击单条信息的跳转链接
                    第3个元素为单条信息后面图片的URL。
        """
        if isinstance(links, tuple):
            links = [links]
        return self.post(
            {
                "msgtype": "feedCard",
                "feedCard": {
                    "links": [
                        {"title": i[0], "messageURL": i[1], "picURL": i[2]}
                        for i in links
                    ]
                },
            }
        )


class AsyncDDBot:
    """钉钉自定义机器人对象(异步)
    :param access_token: 机器人webhook的access_token字段
    :param secret: 机器人的secret字段
    :param logger: 设置为 ``True`` 开启日志或者传入一个 logger 对象用来输出日志,
                    设置为 `False` 来关闭日志，默认为 `True`
    :param timeout: 发起http请求时，允许等待响应的时间
    """

    def __init__(self, access_token: str, secret: str, logger=True, timeout=20):
        self.access_token = access_token
        self.secret = secret
        self.client = httpx.AsyncClient(timeout=timeout)

        if not isinstance(logger, bool):
            self.logger = logger
        else:
            self.logger = default_logger
            if not logging.root.handlers and self.logger.level == logging.NOTSET:
                if logger:
                    self.logger.setLevel(logging.INFO)
                else:
                    self.logger.setLevel(logging.ERROR)
                h = logging.StreamHandler()
                h.setFormatter(
                    logging.Formatter("%(asctime)s[%(levelname)s] %(message)s")
                )
                self.logger.addHandler(h)

    @property
    def webhook(self) -> str:
        """返回完整的webhook地址"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return httpx.URL(
            "https://oapi.dingtalk.com/robot/send",
            {
                "timestamp": timestamp,
                "sign": sign,
                "access_token": self.access_token,
            },
        )

    async def post(self, payload: dict) -> Union[dict, str]:
        """发送POST请求
        :param payload: 需要上报的数据(JSON格式)
        :return: 返回响应数据JSON解码后的字典，如果解码失败返回响应的文本内容,
                 如果请求出错，返回None
        """
        try:
            resp = await self.client.post(self.webhook, json=payload)
            resp.raise_for_status()
        except Exception:
            self.logger.error(traceback.format_exc())
        else:
            try:
                res = resp.json()
            except Exception:
                self.logger.error("请求返回格式错误")
                res = resp.text
            else:
                if res["errcode"] == 0:
                    self.logger.info(
                        "请求成功 errcode: {errcode}, errmsg: {errmsg}".format(**res)
                    )
                elif res["errcode"] == 310000:
                    self.logger.error(
                        "校验未通过 errcode: {errcode}, errmsg: {errmsg}".format(**res)
                    )
                else:
                    self.logger.error(
                        "API错误 errcode: {errcode}, errmsg: {errmsg}".format(**res)
                    )
            return res
        return None

    async def text(
        self, content: str, atMobiles: Union[int, List[int]] = None, isAtAll=False
    ):
        """发送文本(text)类型信息
        :param content: 消息内容
        :param atMobiles: 被@人的手机号，可以是单个手机号或手机号列表
        :param isAtAll: 是否@所有人
        """
        if atMobiles is None:
            atMobiles = []
        elif isinstance(atMobiles, Sequence):
            atMobiles = list(atMobiles)
        else:
            atMobiles = [atMobiles]
        return await self.post(
            {
                "msgtype": "text",
                "text": {"content": content},
                "at": {"atMobiles": [str(i) for i in atMobiles], "isAtAll": isAtAll},
            }
        )

    async def link(self, title: str, text: str, messageURL: str, picURL: str = ""):
        """发送链接(link)类型消息
        :param title: 消息标题
        :param text: 消息内容
        :param messageURL: 点击消息跳转的URL
        :param picURL: 图片URL
        """
        return await self.post(
            {
                "msgtype": "link",
                "link": {
                    "text": text,
                    "title": title,
                    "picUrl": picURL,
                    "messageUrl": messageURL,
                },
            }
        )

    async def markdown(
        self,
        title: str,
        text: str,
        atMobiles: Union[int, List[int]] = None,
        isAtAll=False,
    ):
        """发送Markdown类型消息
        :param title: 首屏会话透出的展示内容。
        :param text: markdown格式的消息。
        :param atMobiles: 被@人的手机号，可以是单个手机号或手机号列表
        :param isAtAll: 是否@所有人
        """
        if atMobiles is None:
            atMobiles = []
        elif isinstance(atMobiles, Sequence):
            atMobiles = list(atMobiles)
        else:
            atMobiles = [atMobiles]
        return await self.post(
            {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": text},
                "at": {"atMobiles": [str(i) for i in atMobiles], "isAtAll": isAtAll},
            }
        )

    async def wholeActionCard(
        self, title: str, text: str, singleTitle: str, singleURL: str, btnOrientation=0
    ):
        """发送整体跳转ActionCard类型消息
        :param title: 首屏会话透出的展示内容。
        :param text: markdown格式的消息。
        :param singleTitle: 单个按钮的标题
        :param singleURL: 点击singleTitle按钮触发的URL。
        :param btnOrientation: 0：按钮竖直排列 1：按钮横向排列
        """
        return await self.post(
            {
                "actionCard": {
                    "title": title,
                    "text": text,
                    "btnOrientation": btnOrientation,
                    "singleTitle": singleTitle,
                    "singleURL": singleURL,
                },
                "msgtype": "actionCard",
            }
        )

    async def separatedActionCard(
        self,
        title: str,
        text: str,
        btns: Union[Tuple[str, str], List[Tuple[str, str]]],
        btnOrientation=0,
    ):
        """发送独立跳转ActionCard类型消息
        :param title: 首屏会话透出的展示内容。
        :param text: markdown格式的消息。
        :param btns: 按钮。一个元组或多个元组列表，每个元组含有2个元素
                     第1个元素为按钮标题、第2个元素为点击按钮触发的URL。
        :param btnOrientation: 0：按钮竖直排列 1：按钮横向排列
        """
        if isinstance(btns, tuple):
            btns = [btns]
        return await self.post(
            {
                "msgtype": "actionCard",
                "actionCard": {
                    "title": title,
                    "text": text,
                    "hideAvatar": "0",
                    "btnOrientation": btnOrientation,
                    "btns": [{"title": i[0], "actionURL": i[1]} for i in btns],
                },
            }
        )

    async def feedCard(
        self, links: Union[Tuple[str, str, str], List[Tuple[str, str, str]]]
    ):
        """发送FeedCard类型消息
        :param links: 信息。一个元组或多个元组列表，每个元组含有3个元素
                    第1个元素为单条信息文本、第2个元素为点击单条信息的跳转链接
                    第3个元素为单条信息后面图片的URL。
        """
        if isinstance(links, tuple):
            links = [links]
        return await self.post(
            {
                "msgtype": "feedCard",
                "feedCard": {
                    "links": [
                        {"title": i[0], "messageURL": i[1], "picURL": i[2]}
                        for i in links
                    ]
                },
            }
        )
