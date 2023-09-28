from video_block_talk_zone import *

if __name__ == "__main__":
    video_block = VideoBlock()
  
    # 输入视频路径，替换成自己的
    s_video_in_url = r'video/test.mp4'
    # 输出视频路径
    s_video_out_url = r'video/test_block_talk_zone.mp4'

    n_ret, s_run_msg, o_video_info = video_block.block_video_faster(s_video_in_url, s_video_out_url)
    print(n_ret)
    print(s_run_msg)
    print(o_video_info)
