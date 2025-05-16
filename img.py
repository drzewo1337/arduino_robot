import cv2
import numpy as np
import torch
import torchvision.transforms as transforms


class ImageInfo:
    def __init__(self):
        #img data
        self.img = None
        self.threshold_light = 50
        self.threshold_dist = 1.0
        self.threshold_area = 10
        self.light = False
        self.collision = False

        #model to detect collision
        self.model_path = 'dpt_levit_224.pt'
        self.path = torch.load(self.model_path,map_location=torch.device('cpu'))
        self.midas = torch.hub.load("intel-isl/MiDaS", "MiDaS")
        self.midas.to(torch.device('cpu'))
        self.midas.eval()


    def update(self,img):
        """ replaces new img frame """

        self.img = img


    def check_luminosity(self):
        """ checks if flashlight is needed
            if self.light = True -> turn on flashlight
            if self.light = False -> turn off flashlight """

        processed = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(processed)
        avg_v = np.mean(v)
        percent = (avg_v/255)*100

        if percent < self.threshold_light:
            self.light = True

        elif percent >=self.threshold_light:
            self.light = False

    def check_collision(self):
        """ checks if collision might occur by checking img deph
            if self.collision = True -> collision risk
            if self.collision = False -> no collision risk """

        img_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (384, 384))
        img_tensor = transforms.ToTensor()(img_resized).unsqueeze(0)

        with torch.no_grad():
            prediction = self.midas(img_tensor.to(torch.device('cpu')))

        depth_map = prediction.squeeze().cpu().numpy()

        depth_map_resized = cv2.resize(depth_map, (self.img.shape[1], self.img.shape[0]))

        depth_map_normalized = (depth_map_resized - depth_map_resized.min()) / (
                    depth_map_resized.max() - depth_map_resized.min()) * 255

        depth_map_uint8 = depth_map_normalized.astype(np.uint8)

        depth_map_uint8_color = cv2.cvtColor(depth_map_uint8, cv2.COLOR_GRAY2BGR)

        img_with_depth = np.hstack((self.img, depth_map_uint8_color))
        img_with_depth = cv2.cvtColor(img_with_depth, cv2.COLOR_BGR2GRAY)

        obstacle_mask = img_with_depth < self.threshold_dist
        contours, _ = cv2.findContours(obstacle_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.collision = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.threshold_area:
                self.collision = True

    def process_image(self,img):
        """ handles processing """

        self.update(img)
        self.check_luminosity()
        self.check_collision()
        return self.light, self.collision
