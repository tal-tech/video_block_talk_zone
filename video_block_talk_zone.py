import os
import cv2
import time
import subprocess
import numpy as np

S_NOW_DIR = os.path.dirname(os.path.abspath(__file__))
B_DEBUG = True

class VideoBlock:
    def __init__(self):
        s_template_img_url = os.path.join(S_NOW_DIR, 'template.jpg')
       
        # self.s_ffmpeg = r'D:\Dev_Utils\_Utils\ffmepg\ffmpeg'  # 绝对路径
        # self.s_ffmpeg = os.path.join(S_NOW_DIR, 'ffmpeg_bin/ffmpeg-linux64-v4.1')

        # B_DEBUG and print("ffmpeg %s" % self.s_ffmpeg)

        self.np_template_raw = cv2.imread(s_template_img_url, -1)
        
        self.np_template_in = None
        self.n_w, self.n_h = 0, 0
        self.n_zone_w, self.n_zone_h = 0, 0

        self.fourcc_mp4 = cv2.VideoWriter_fourcc(*'MP4V')
        self.kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32) #定义一个核

    def get_block_info(self, s_video_in_url):
        lo_block_info = []

        video_reader = cv2.VideoCapture(s_video_in_url)
        fps = video_reader.get(5) # 帧速率
        frameCount = video_reader.get(7)  # 视频文件的帧
        duration = frameCount/fps # 获取时间长度

        o_video_info = {"fps":fps, "frame":frameCount, "duration":duration}


        self.n_w, self.n_h = int(video_reader.get(3)), int(video_reader.get(4))

        B_DEBUG and print("fps: ", fps)
        B_DEBUG and print("frame cnt: ", frameCount)
        B_DEBUG and print("video duration ", duration)

        np_pure_black = None
        if self.n_w == 1280 or self.n_h == 720:
            np_pure_black = np.zeros((720, 1280, 3))
            self.n_zone_w, self.n_zone_h = 960, 240
            self.np_template_in = cv2.resize(self.np_template_raw, (320, 480), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        elif self.n_w == 1920 or self.n_h == 1080:
            np_pure_black = np.zeros((1080, 1920, 3))
            self.n_zone_w, self.n_zone_h = 1440, 360
            self.np_template_in = cv2.resize(self.np_template_raw, (480, 720), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        elif self.n_w == 1056 or self.n_h == 600:
            np_pure_black = np.zeros((600, 1050, 3))
            self.n_zone_w, self.n_zone_h = 800, 193
            self.np_template_in = cv2.resize(self.np_template_raw, (256, 407), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        else:
            np_pure_black = np.zeros((self.n_h, self.n_w, 3))
            self.n_zone_w = (3 * self.n_w) // 4
            self.n_zone_h = self.n_h // 3
            self.np_template_in = cv2.resize(self.np_template_raw, (self.n_w - self.n_zone_w, self.n_h - self.n_zone_h), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            
        for i in range(int(frameCount)):
            o_block_info = {"f": i+1, "qr":[], "talk": True}
            lo_block_info.append(o_block_info)

        n_ith_frame = 0
        n_detect_step = 10
        n_batch_step = 150

        l_batch_frame_data = []
        l_detect_qr_zone = []

        while True:
            n_ith_frame += 1
            success, np_frame_now = video_reader.read()
            
            if n_ith_frame <= 30:
                b_need_block_talk_zone = not ((np_frame_now == np_pure_black).all())
                if n_ith_frame - 1 < len(lo_block_info):
                    lo_block_info[n_ith_frame - 1]["talk"] = b_need_block_talk_zone
            else:
                break

        # for e in lo_block_info:
        #     print(e)

        # print("len lo_block_info ", len(lo_block_info))
        # print("frame cnt: ", frameCount)
        # print("memery size: ", sys.getsizeof(lo_block_info))

        return 0, lo_block_info, o_video_info


    def block_img(self, np_img_raw, o_block_info):
        if o_block_info["talk"]:
            np_img_raw[self.n_zone_h:, self.n_zone_w:, :] = self.np_template_in
        return np_img_raw


    def block_video_faster(self, s_video_in_url, s_video_out_url):
        n_ret, s_run_msg = 0, "Success"
        t_start = time.time()

        # 得到每一帧需频闭的信息
        t1 = time.time()
        n_ret, lo_block_info, o_video_info = self.get_block_info(s_video_in_url)
        t2 = time.time()
        print("get block info ", t2 - t1)

        # 对每一帧图像进行处理
        if n_ret == 0: 
            # get all frame and process each frame
            # fourcc_h264 = cv2.VideoWriter_fourcc('H','2','6','4')
            t1 = time.time()
            s_video_out_tmp_url = s_video_out_url.replace(".mp4", "_tmp.mp4")
            print(s_video_out_tmp_url)

            # try:
            video_reader = cv2.VideoCapture(s_video_in_url)
            video_writer = cv2.VideoWriter(s_video_out_tmp_url, self.fourcc_mp4, o_video_info["fps"], (self.n_w, self.n_h))  
            n_ith_frame = 0
            while True:
                n_ith_frame += 1
                success, np_frame_now = video_reader.read()  
                if not success:
                    break
                np_frame_out = self.block_img(np_frame_now, lo_block_info[n_ith_frame - 1])
                video_writer.write(np_frame_out)
            video_reader.release()
            video_writer.release()
            # except Exception as e:
            #     s_run_msg = str(e)
            #     n_ret = -1

        # get audio from input video   
        t1 = time.time()
        s_aac_url = ""
        if n_ret == 0: 
            try:
                s_aac_url = s_video_in_url.replace(".mp4", ".aac")
                if os.path.exists(s_aac_url):
                    os.remove(s_aac_url)
                s_ffmpeg_cmd = "ffmpeg -i %s -vn -y -acodec copy %s" % (s_video_in_url, s_aac_url)
                # s_ffmpeg_cmd = "%s -i %s -vn -y -acodec copy %s  -loglevel quiet" % (self.s_ffmpeg , s_video_in_url, s_aac_url)
                print(s_ffmpeg_cmd) 
                subprocess.call(s_ffmpeg_cmd, shell=True) # 调用命令行进行转换
            except Exception as e:
                s_run_msg = str(e)
                n_ret = -1
        t2 = time.time()
        print("get audio time ", t2 - t1)
       

        # mix audio to video
        t1 = time.time()
        if n_ret == 0:
            try:
                if os.path.exists(s_video_out_url):
                    os.remove(s_video_out_url)
                # s_ffmpeg_cmd = "%s -i %s -i %s -vcodec h264  -bsf:a aac_adtstoasc -strict -2 %s" % (self.s_ffmpeg , s_video_out_tmp_url, s_aac_url, s_video_out_url)
                s_ffmpeg_cmd = "ffmpeg -i %s -i %s -vcodec h264 -acodec copy %s" % (s_video_out_tmp_url, s_aac_url, s_video_out_url)
                
                print(s_ffmpeg_cmd) 
                subprocess.call(s_ffmpeg_cmd, shell=True) # 调用命令行进行转换
            except Exception as e:
                s_run_msg = str(e)
                n_ret = -1
        t2 = time.time()
        print("get new video time ", t2 - t1)

        if os.path.exists(s_video_out_tmp_url): 
            os.remove(s_video_out_tmp_url)

        if os.path.exists(s_aac_url): 
            os.remove(s_aac_url)

        t_end = time.time()
        print("duration ", o_video_info["duration"])
        print("total cost time ", t_end - t_start)
        print()


        o_video_info["cost_time"] = t_end - t_start
        return n_ret, s_run_msg, o_video_info
