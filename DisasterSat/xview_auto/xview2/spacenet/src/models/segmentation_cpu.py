#!/usr/bin/env python

#####################################################################################################################################################################
# xView2                                                                                                                                                            #
# Copyright 2019 Carnegie Mellon University.                                                                                                                        #
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO    #
# WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY,          # 
# EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, # 
# TRADEMARK, OR COPYRIGHT INFRINGEMENT.                                                                                                                             #
# Released under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.                                                 #
# [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use  #
# and distribution.                                                                                                                                                 #
# This Software includes and/or makes use of the following Third-Party Software subject to its own license:                                                         #
# 1. SpaceNet (https://github.com/motokimura/spacenet_building_detection/blob/master/LICENSE) Copyright 2017 Motoki Kimura.                                         #
# DM19-0988                                                                                                                                                         #
#####################################################################################################################################################################

import numpy as np
import cv2
import math

import chainer
import chainer.functions as F
from chainer import cuda, serializers, Variable
import os
import sys
#from unet import UNet
#sys.path.append('../src/models')
#this is ugly but had to add UNET to this class since I couldn't import
#from unet import UNet as UNET

class SegmentationModel:
    
    def __init__(self, model_path, mean):

        # Load model
        self.__model = UNet()
        #self.__model =UNET()
        
        serializers.load_npz(model_path, self.__model)

        # Add height and width dimensions to mean 
        self.__mean = mean[np.newaxis, np.newaxis, :]

    def apply_segmentation(self, image):
        
        image_in, crop = self.__preprocess(image)
        
        chainer.using_config('device', -1)

        with chainer.using_config('train', False):
            score = self.__model.forward(image_in)


        score = F.softmax(score)
        score = score.data[0]

        top, left, bottom, right = crop
        score = score[:, top:bottom, left:right]

        return score

    def apply_segmentation_to_mosaic(self, mosaic, grid_px=800, tile_overlap_px=200):
        
        h, w, _ = mosaic.shape

        assert ((grid_px + tile_overlap_px * 2) % 16 == 0), "(grid_px + tile_overlap_px * 2) must be divisible by 16"

        pad_y1 = tile_overlap_px
        pad_x1 = tile_overlap_px

        n_y = int(float(h) / float(grid_px))
        n_x = int(float(w) / float(grid_px))
        pad_y2 = n_y * grid_px + 2 * tile_overlap_px - h - pad_y1
        pad_x2 = n_x * grid_px + 2 * tile_overlap_px - h - pad_x1

        mosaic_padded = np.pad(mosaic, ((pad_y1, pad_y2), (pad_x1, pad_x2), (0, 0)), 'symmetric')

        H, W, _ = mosaic_padded.shape
        score_padded = np.zeros(shape=[self.__model.class_num, H, W], dtype=np.float32)

        for yi in range(n_y):
            for xi in range(n_x):
                
                top = yi * grid_px
                left = xi * grid_px
                bottom = top + grid_px + 2 * tile_overlap_px
                right = left + grid_px + 2 * tile_overlap_px

                tile = mosaic_padded[top:bottom, left:right]

                score_tile = self.apply_segmentation(tile)

                score_padded[:, top:bottom, left:right] = score_tile

        score = score_padded[:, pad_y1:-pad_y2, pad_x1:-pad_x2]

        return score

    def __preprocess(self, image):

        h, w, _ = image.shape
        h_padded = int(math.ceil(float(h) / 16.0) * 16)
        w_padded = int(math.ceil(float(w) / 16.0) * 16)

        pad_y1 = (h_padded - h) // 2
        pad_x1 = (w_padded - w) // 2
        pad_y2 = h_padded - h - pad_y1
        pad_x2 = w_padded - w - pad_x1

        image_padded = np.pad(image, ((pad_y1, pad_y2), (pad_x1, pad_x2), (0, 0)), 'symmetric')
        image_in = (image_padded - self.__mean) / 255.0
        image_in = image_in.transpose(2, 0, 1)
        image_in = image_in[np.newaxis, :, :, :]
        image_in = Variable(np.asarray(image_in, dtype=np.float32))

        top, left = pad_y1, pad_x1
        bottom, right = top + h, left + w

        return image_in, (top, left, bottom, right)

    #!/usr/bin/env python

#####################################################################################################################################################################
# xView2                                                                                                                                                            #
# Copyright 2019 Carnegie Mellon University.                                                                                                                        #
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO    #
# WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY,          # 
# EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, # 
# TRADEMARK, OR COPYRIGHT INFRINGEMENT.                                                                                                                             #
# Released under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.                                                 #
# [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use  #
# and distribution.                                                                                                                                                 #
# This Software includes and/or makes use of the following Third-Party Software subject to its own license:                                                         #
# 1. SpaceNet (https://github.com/motokimura/spacenet_building_detection/blob/master/LICENSE) Copyright 2017 Motoki Kimura.                                         #
# DM19-0988                                                                                                                                                         #
#####################################################################################################################################################################

import chainer
import chainer.functions as F
import chainer.links as L



class UNet(chainer.Chain):

    def __init__(self, class_num=2, ignore_label=255):

        self.__class_num = class_num
        self.__ignore_label = ignore_label

        super(UNet, self).__init__(
            c0=L.Convolution2D(3, 32, 3, 1, 1),
            c1=L.Convolution2D(32, 64, 4, 2, 1),
            c2=L.Convolution2D(64, 64, 3, 1, 1),
            c3=L.Convolution2D(64, 128, 4, 2, 1),
            c4=L.Convolution2D(128, 128, 3, 1, 1),
            c5=L.Convolution2D(128, 256, 4, 2, 1),
            c6=L.Convolution2D(256, 256, 3, 1, 1),
            c7=L.Convolution2D(256, 512, 4, 2, 1),
            c8=L.Convolution2D(512, 512, 3, 1, 1),

            dc8=L.Deconvolution2D(1024, 512, 4, 2, 1),
            dc7=L.Convolution2D(512, 256, 3, 1, 1),
            dc6=L.Deconvolution2D(512, 256, 4, 2, 1),
            dc5=L.Convolution2D(256, 128, 3, 1, 1),
            dc4=L.Deconvolution2D(256, 128, 4, 2, 1),
            dc3=L.Convolution2D(128, 64, 3, 1, 1),
            dc2=L.Deconvolution2D(128, 64, 4, 2, 1),
            dc1=L.Convolution2D(64, 32, 3, 1, 1),
            dc0=L.Convolution2D(64, class_num, 3, 1, 1),

            bnc0=L.BatchNormalization(32),
            bnc1=L.BatchNormalization(64),
            bnc2=L.BatchNormalization(64),
            bnc3=L.BatchNormalization(128),
            bnc4=L.BatchNormalization(128),
            bnc5=L.BatchNormalization(256),
            bnc6=L.BatchNormalization(256),
            bnc7=L.BatchNormalization(512),
            bnc8=L.BatchNormalization(512),

            bnd8=L.BatchNormalization(512),
            bnd7=L.BatchNormalization(256),
            bnd6=L.BatchNormalization(256),
            bnd5=L.BatchNormalization(128),
            bnd4=L.BatchNormalization(128),
            bnd3=L.BatchNormalization(64),
            bnd2=L.BatchNormalization(64),
            bnd1=L.BatchNormalization(32)
        )


    def forward(self, x):

        e0 = F.relu(self.bnc0(self.c0(x)))
        e1 = F.relu(self.bnc1(self.c1(e0)))
        e2 = F.relu(self.bnc2(self.c2(e1)))
        del e1
        e3 = F.relu(self.bnc3(self.c3(e2)))
        e4 = F.relu(self.bnc4(self.c4(e3)))
        del e3
        e5 = F.relu(self.bnc5(self.c5(e4)))
        e6 = F.relu(self.bnc6(self.c6(e5)))
        del e5
        e7 = F.relu(self.bnc7(self.c7(e6)))
        e8 = F.relu(self.bnc8(self.c8(e7)))

        d8 = F.relu(self.bnd8(self.dc8(F.concat([e7, e8]))))
        del e7, e8
        d7 = F.relu(self.bnd7(self.dc7(d8)))
        del d8
        d6 = F.relu(self.bnd6(self.dc6(F.concat([e6, d7]))))
        del d7, e6
        d5 = F.relu(self.bnd5(self.dc5(d6)))
        del d6
        d4 = F.relu(self.bnd4(self.dc4(F.concat([e4, d5]))))
        del d5, e4
        d3 = F.relu(self.bnd3(self.dc3(d4)))
        del d4
        d2 = F.relu(self.bnd2(self.dc2(F.concat([e2, d3]))))
        del d3, e2
        d1 = F.relu(self.bnd1(self.dc1(d2)))
        del d2
        d0 = self.dc0(F.concat([e0, d1]))

        return d0


    def __call__(self, x, t):

        h = self.forward(x)
        
        loss = F.softmax_cross_entropy(h, t, ignore_label=self.__ignore_label)
        accuracy = F.accuracy(h, t, ignore_label=self.__ignore_label)
        
        chainer.report({'loss': loss, 'accuracy': accuracy}, self)
        
        return loss

        
    @property
    def class_num(self):
        return self.__class_num
    
