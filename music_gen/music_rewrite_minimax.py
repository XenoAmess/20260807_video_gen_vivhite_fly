import requests
import json
import os

url = "https://api.minimaxi.com/v1/music_generation"
api_key = os.environ.get("MINIMAX_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

cover_feature_id = "c5f2c2c2cc527f12ea2aa9187f79472d"

# 使用上一步返回的 cover_feature_id
# 根据需要修改提取的歌词
modified_lyrics = '''
[Intro]

[Verse 1]
Ladies and gentlemen
I told you
It's 白绮
It's 白绮
It's 白绮
No more Vivhite
It's 白绮
It's 白绮
充满能量
使我能够飞翔

[Chorus 1]
I can fly
yeah
I can fly
我能飞
Do you believe you can
你是绮明星吗
I can
I can fly
我能飞
If you believe you can
是绮明星就可以

[Verse 2]
白子姐能飞
白子姐能飞
白子姐能飞
白绮
绮明星才对
学数学才飞
平胸就是美
白绮

[Verse 3]
我在vtuber圈就像个弟弟
遇到困难直接放弃
数学家不想再做题
我用队友来打地基
所以绮明星出生就能飞上天
天上有好多神仙
但是只在白绮直播间里面

[Chorus 2]

[Chorus 3]
谢谢
'''

payload = {
    "model": "music-cover",
    "cover_feature_id": cover_feature_id,
    "lyrics": modified_lyrics,
    "prompt": "说唱, 温柔女声",
    "audio_setting": {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "mp3"
    },
    "output_format": "url"
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

print(json.dumps(result, ensure_ascii=False, indent=2))