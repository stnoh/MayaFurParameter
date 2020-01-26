###############################################################################
## normalized-VGG19 and perceptual feature extractor
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import numpy as np
from datetime import datetime

from stNoh import vgg19
from keras import backend as K
import cv2

###############################################################################
# main routine
###############################################################################
if "__main__" == __name__:

    ## prepare normalized VGG19 with max pooling layers
    model_max = vgg19.VGG19(avgPooling=False)

    ############################################################
    ## every 2nd conv. layer in each block: "style feature"
    ############################################################
    feature_layers_max = ['block1_conv2', 'block2_conv2', 'block3_conv2', 'block4_conv2', 'block5_conv2']
    weight_layers_max  = [1e2, 1e2, 1e2, 1e2, 1e2]
    func_layer_max     = K.function([model_max.input],
                                    [model_max.get_layer(layer).output[0,:,:,:] for layer in feature_layers_max])

    def vgg_max_gray_gram(img_cv2):

        ## convert BGR->GRAY->BGR to cancel color effect
        img_gray = cv2.cvtColor(img_cv2 , cv2.COLOR_BGR2GRAY)
        img_BGR  = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

        t_feature_start = datetime.now()

        ## convert and feed image
        img_keras = vgg19.preprocess_input(img_BGR)
        outputs = func_layer_max([img_keras])
        
        ## get gram matrices at feature layers
        G = []
        for l, _ in enumerate(feature_layers_max):
            G_l = vgg19.np_gram_matrix(outputs[l]) * weight_layers_max[l]
            G.append(G_l)

        t_feature_end = datetime.now()
        t_feature_elapsed = t_feature_end - t_feature_start

        return G, t_feature_elapsed

    def vgg_max_color_gram(img_cv2):

        t_feature_start = datetime.now()

        ## convert and feed image
        img_keras = vgg19.preprocess_input(img_cv2)
        outputs = func_layer_max([img_keras])
        
        ## get gram matrices at feature layers
        G = []
        for l, _ in enumerate(feature_layers_max):
            G_l = vgg19.np_gram_matrix(outputs[l]) * weight_layers_max[l]
            G.append(G_l)

        t_feature_end = datetime.now()
        t_feature_elapsed = t_feature_end - t_feature_start

        return G, t_feature_elapsed 

    ############################################################
    ## define the cost function
    ############################################################
    def calc_cost_func(G_ref, G_dst):
        G_ref_vec   = np.concatenate([G_l.flatten() for G_l in G_ref])
        G_dst_vec   = np.concatenate([G_l.flatten() for G_l in G_dst])
        G_diff = (G_ref_vec - G_dst_vec).reshape(-1)

        return np.sum(G_diff ** 2)
