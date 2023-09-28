# 聊天区域遮挡
video_block_talk_zone

# 问题背景
三分屏聊视频中右下角聊天区中视频需要遮蔽

# 解决方案
三分屏中聊天区一般固定在右下角，直接用图片遮蔽右下角

# 修改测试视频路径
```
demo.py下
# 输入视频路径，替换成自己的
s_video_in_url = r'video/test.mp4'
# 输出视频路径
s_video_out_url = r'video/test_block_talk_zone.mp4'
```

# 环境
详细见requirements.txt

# 测试命令
将一个视频中聊天区遮蔽
```shell
python demo.py
```

# 目前精度
100测试集上100%遮蔽聊天区
