import glob

import cv2
import matplotlib.pyplot as plt

from detector import Detector
from drawer import Drawer
from matcher import Matcher
from preprocessor import Preprocessor

path = './data/Fluo-N2DL-HeLa/Sequence 1/'


def main():
    seq = []
    images = glob.glob(path + '*.tif')
    for i in images:
        image = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        seq.append(image)

    preprocessor = Preprocessor(seq)
    detector = Detector(preprocessor)
    matcher = Matcher(detector)
    drawer = Drawer(matcher, preprocessor)

    masks = preprocessor.get_masks()
    
    print('Generating all frames and cell states...')
    drawer.load()
    print('Successfully loaded all images')
    
    # Save all generated images and their masks to disk
    counter = 1
    for g in drawer.get_gen_images():
        annotated = cv2.imwrite(path + f'gen/{counter}.tif', g)
        mask = cv2.imwrite(path + f'gen/{counter}_mask.tif', masks[counter - 1])
        if not annotated or not mask:
            print(f'Failed to save')
        counter += 1
    print('Saved all images')
    
    # Now standby for user to issue commands for retrieval
    while True:
        string = input('Input a frame and cell ID (optional) separated by a space...\n')
        if string:
            string = string.split(' ')
            frame = int(string[0])
            if len(string) > 1:
                try:
                    id = int(string[1])
                    display_image = drawer.serve(frame, id)
                except ValueError:
                    print(f'Not an integer')
                    display_image = drawer.serve(frame)
            else:
                display_image = drawer.serve(frame)
            # plt.imshow(display_image)
            # plt.axis('off')
            # plt.show()
            # cv2.imshow('image',display_image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        else:
            break

if __name__ == '__main__':
    main()
