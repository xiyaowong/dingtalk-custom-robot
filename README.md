# dingtalk-custom-robot

对钉钉自定义机器人的 API 封装

# Example

```python
import asyncio
import time

from ddbot import AsyncDDBot, DDBot
#####################################################################
# 示例对应官方文档所给出的示例
# https://developers.dingtalk.com/document/app/custom-robot-access
#####################################################################
ACCESS_TOKEN = "机器人的access_token"
SECRET = "机器人的secret"
##################### 同步 #########################
ddbot = DDBot(
    access_token=ACCESS_TOKEN,
    secret=SECRET,
)


def main():
    # text类型
    ddbot.text("我就是我，是不一样的烟火")
    time.sleep(1)
    # link类型
    ddbot.link(
        title="这个即将发布的新版本，创始人xx称它为红树",
        text="时代的火车向前开",
        messageURL="https://www.dingtalk.com/s?__biz=MzA4NjMwMTA2Ng==&mid=2650316842&idx=1&sn=60da3ea2b29f1dcc43a7c8e4a7c97a16&scene=2&srcid=09189AnRJEdIiWVaKltFzNTw&from=timeline&isappinstalled=0&key=&ascene=2&uin=&devicetype=android-23&version=26031933&nettype=WIFI",
    )
    time.sleep(1)
    # markdown类型
    ddbot.markdown(
        title="杭州天气",
        text="#### 杭州天气 @150XXXXXXXX \n> 9度，西北风1级，空气良89，相对温度73%\n> ![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png)\n> ###### 10点20分发布 [天气](https://www.dingtalk.com) \n",
    )
    time.sleep(1)
    # 整体跳转ActionCard类型
    ddbot.wholeActionCard(
        title="乔布斯 20 年前想打造一间苹果咖啡厅，而它正是 Apple Store 的前身",
        text=(
            "![screenshot](https://gw.alicdn.com/tfs/TB1ut3xxbsrBKNjSZFpXXcXhFXa-846-786.png) "
            "### 乔布斯 20 年前想打造的苹果咖啡厅 "
            "Apple Store 的设计正从原来满满的科技感走向生活化，而其生活化的走向其实可以追溯到 20 年前苹果一个建立咖啡馆的计划"
        ),
        singleTitle="阅读全文",
        singleURL="https://www.dingtalk.com/",
    )
    time.sleep(1)
    # 独立跳转ActionCard类型
    ddbot.separatedActionCard(
        title="我 20 年前想打造一间苹果咖啡厅，而它正是 Apple Store 的前身",
        text="![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png) \n\n #### 乔布斯 20 年前想打造的苹果咖啡厅 \n\n Apple Store 的设计正从原来满满的科技感走向生活化，而其生活化的走向其实可以追溯到 20 年前苹果一个建立咖啡馆的计划",
        btns=[
            ("内容不错", "https://www.dingtalk.com/"),
            ("不感兴趣", "https://www.dingtalk.com/"),
        ],
    )
    time.sleep(1)
    # FeedCard类型
    ddbot.feedCard(
        links=[
            (
                "时代的火车向前开1",
                "https://www.dingtalk.com/",
                "https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png",
            ),
            (
                "时代的火车向前开2",
                "https://www.dingtalk.com/",
                "https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png",
            ),
        ]
    )


# main()


##################### 异步 ##########################
addbot = AsyncDDBot(ACCESS_TOKEN, SECRET)


async def amain():
    # text类型
    await addbot.text("我就是我，是不一样的烟火")
    await asyncio.sleep(1)
    # link类型
    await addbot.link(
        title="这个即将发布的新版本，创始人xx称它为红树",
        text="时代的火车向前开",
        messageURL="https://www.dingtalk.com/s?__biz=MzA4NjMwMTA2Ng==&mid=2650316842&idx=1&sn=60da3ea2b29f1dcc43a7c8e4a7c97a16&scene=2&srcid=09189AnRJEdIiWVaKltFzNTw&from=timeline&isappinstalled=0&key=&ascene=2&uin=&devicetype=android-23&version=26031933&nettype=WIFI",
    )


asyncio.run(amain())
```

# LICENSE

MIT
