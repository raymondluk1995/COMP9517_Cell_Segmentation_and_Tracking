"""
Preprocessor processes the raw input images and get their masks.
Deep learning methods and thresholding algorithm are provided for the user to choose
"""

import cv2
import numpy as np 
import tensorflow as tf
from scipy import ndimage as ndi 
from libtiff import TIFF
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
import sys 
import ast
sys.path.insert(0, './jnet_inference')
sys.path.insert(0, './deepwater_inference')
from jnet_inference.nets import Model,load_model_from_file
from jnet_inference.evaluate import evaluate
from jnet_inference.dataset import JNet_Cells
from dw_config import load_config
from deepwater_inference.src.deepwater_object import DeepWater

class Preprocessor:
    def __init__(self, images,params):
        # Save original images file names
        self.remaining_img = len(images)
        self.original_images = images
        self.params = params 
        self.params.cuda = params.cuda 
        self.model = None 
        self.dataset = None 
         
        if (params.dataset=="DIC-C2DH-HeLa" and params.nn_method=="JNet"):
            self.model = load_model_from_file(params.model_file)
        
        # Preprocess images 
        self.masks = self.preprocess(images)
        # Counter is used to keep track of current image and mask on next() call
        self.counter = 0
        # Keep track if finished; 1 = not done
        self.status = 1
    # Process an array of original images and return an array of masks
    def preprocess(self,images):
        processed = []
        if (self.params.dataset=="DIC-C2DH-HeLa"):
            processed = self.get_DIC_masks(images)
        elif(self.params.dataset=="Fluo-N2DL-HeLa"):
            processed = self.get_Fluo_masks(images)
        elif(self.params.dataset=="PhC-C2DL-PSC"):
            processed = self.get_PHC_masks(images)
        else:
            raise ValueError("Dataset "+self.params.dataset+" is not supported!")
        return processed

    def get_DIC_masks(self,images):
        def post_process(mask): # Use morphological opening operation and watershed to improve the JNet Masks
            ret, mask_threh = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            blurred = cv2.GaussianBlur(mask_threh, (9,9),0)
            kernel=np.ones((5,5),np.uint8) 
            erosion=cv2.erode(blurred,kernel,iterations=1) 
            dilation=cv2.dilate(erosion,kernel,iterations=1) 
            ret, thresh = cv2.threshold(dilation, 190, 255, cv2.THRESH_BINARY)
            distance = ndi.distance_transform_edt(thresh)
            local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((55,55)),labels=thresh)
            markers = ndi.label(local_maxi)[0]
            labels = watershed(-distance, markers, mask=thresh)
            return (labels)

        if (self.params.nn_method=="JNet"):
            dataset=JNet_Cells(self.original_images,[],self.params.dt_bound,\
                ast.literal_eval(self.params.resolution_levels),load_to_memory=bool(self.params.load_dataset_to_ram))
            dic_masks = evaluate(self.model,dataset,self.params) 
            new_masks = [] 
            for mask in dic_masks:
                new_masks.append(post_process(mask))
            return (new_masks)
        elif(self.params.nn_method=="DeepWater"):
            config = load_config(self.params,mode=2)
            model = DeepWater(config)
            print("Start segmentation...")
            return (model.test())
        else:
            raise ValueError("Neural Network Method should be JNet or DeepWater!")

    def get_Fluo_masks(self,images):
        # Use thresholding algorithm to segment cells
        def thresholding_batch_process_2(img_path): 
            image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            kernel = 11
            img = cv2.GaussianBlur(image, (kernel, kernel), 0)
            hist, bins = np.histogram(img.flatten(), 256, [0, 256])
            th = np.where(hist == np.max(hist))[0]
            ret, thresh = cv2.threshold(img, th[0] + 1, 255, cv2.THRESH_BINARY)
            thresh = cv2.erode(thresh, np.ones((9, 9)))
            thresh = cv2.dilate(thresh, np.ones((9, 9)))
            return thresh
        fluo_masks = [] 
        for img_path in self.original_images:
            fluo_masks.append(thresholding_batch_process_2(img_path))
        return(fluo_masks)


    def get_PHC_masks(self,images):
        # Use thresholding algorithm to segment cells
        def d3_threshold_seg(img_path):
            img = cv2.imread(img_path,cv2.IMREAD_GRAYSCALE) 
            img = cv2.erode(img,np.ones((2,2)))
            kernel = 3
            img  =cv2.GaussianBlur(img,(kernel,kernel),0)
            hist,bins = np.histogram(img.flatten(),256,[0,256])
            th  = np.where(hist ==np.max(hist))
            th = np.array([th[0].max()]) 
            ret, thresh = cv2.threshold(img,th+20,255,cv2.THRESH_BINARY)
            return (thresh)

        if (self.params.nn_method == "DeepWater"):
            config = load_config(self.params,mode=2)
            model = DeepWater(config)
            print("Start segmentation...")
            return (model.test()) 
        else:
            phc_masks = []
            for img_path in images:
                phc_masks.append(d3_threshold_seg(img_path))
            return(phc_masks)

    
    # Mask Getter
    def get_masks(self):
        return self.masks
            
    def next(self):

        # Indicate when done
        if self.counter >= self.remaining_img - 1:
            self.status = 0

        # Serves the next image and its mask
        image = cv2.imread(self.original_images[self.counter],cv2.IMREAD_GRAYSCALE)
        mask = self.masks[self.counter]
        self.counter += 1
        return image, mask
       