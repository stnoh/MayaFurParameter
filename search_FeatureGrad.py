###############################################################################
## Fur parameter search by Feature Space Gradient Descent
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds

import traceback
import shutil, os
from datetime import datetime
from collections import OrderedDict

import numpy as np
import cv2
from scipy import optimize ## minimize_scalar (line search)

from stNoh import FurParam
import Misc


###############################################################################
## optimization routine
###############################################################################
def GradientDescent(
        get_feature_func, calc_cost_func, render_and_load,
        convert_param_func, params01_vec_dst,
        folder_path, image_ext, opt_params_dict={},
    ):

    ############################################################
    ## prepara optimization routine
    ############################################################

    ## set constants for optimization in advance
    max_iter   = 30   if opt_params_dict.get('max_iter') is None else opt_params_dict['max_iter']
    max_step   = 20   if opt_params_dict.get('max_step') is None else opt_params_dict['max_step']
    delta      = 0.10 if opt_params_dict.get('delta')    is None else opt_params_dict['delta']

    ## prepare reference image & get perceptual feature
    path_img_ref = folder_path + "/_ref_image.{0}".format(image_ext)
    img_ref_cv2  = cv2.imread(path_img_ref)
    G_ref, _     = get_feature_func(img_ref_cv2)
    G_ref_vec    = np.concatenate([G_ref_l.flatten() for G_ref_l in G_ref])

    Misc.show_text_on_image_cv2(img_ref_cv2, "", "reference")
    
    ## get elapsed time
    global t_render_elapsed
    global t_imageio_elapsed
    global t_feature_elapsed

    ############################################################
    ## run optimization loop
    ############################################################
    global success
    success = True

    ## initial cost = Infinity (Unknown)
    Cost_best  = np.inf
    params_01_vec_best = params01_vec_dst[:]

    ## initial residual = Infinity (Unknown)
    Res_prev   = np.inf
    num_params = len(params01_vec_dst)

    ## start the progress bar here
    maxValue = (max_iter+1) * (num_params + max_step)
    cmds.progressWindow(isInterruptable=1, minValue=0, maxValue=maxValue)

    for num_iter in range(max_iter):
        params_dict = convert_param_func(params01_vec_dst)

        ############################################################
        ## 0) current parameter image & get perceptual feature
        ############################################################
        path_dst = '{0}/iter_{1:04d}'.format(folder_path, num_iter)
        img_dst_cv2, t_render, t_imageio = render_and_load(params_dict, path_dst)
        G_dst, t_feature = get_feature_func(img_dst_cv2)
        G_dst_vec = np.concatenate([G_l.flatten() for G_l in G_dst])

        Cost_prev = calc_cost_func(G_ref, G_dst)

        ## get elapsed time
        t_render_elapsed  += t_render
        t_imageio_elapsed += t_imageio
        t_feature_elapsed += t_feature

        ## show information on the image
        img_text = "Cost: {0}\n#iter {1}".format(Cost_prev, num_iter)
        Misc.show_text_on_image_cv2(img_dst_cv2, img_text, "target")

        ## change the best result
        if  Cost_prev < Cost_best:
            Cost_best = Cost_prev
            params_01_vec_best = params01_vec_dst[:]

        ############################################################
        ## 1) construct matrix A = (N x 15) from numerical gradients
        ############################################################
        A = np.zeros(( len(G_ref_vec) , num_params))

        for ind_param in range(num_params):

            ## select sign for delta increment
            params01_vec_d = []
            params01_vec_d[:] = params01_vec_dst
            increment = +delta if params01_vec_dst[ind_param] < 0.5 else -delta

            ## increment/decrement small delta
            params01_vec_d[ind_param] += increment
            params_d_dict = convert_param_func(params01_vec_d)

            ########################################
            ## move to a single direction & render
            ########################################
            path_dst_d = '{0}/grad/iter_{1:04d}_{2:02d}'.format(folder_path, num_iter, ind_param)
            img_dst_d_cv2, t_render, t_imageio = render_and_load(params_d_dict, path_dst_d)
            G_dst_d, t_feature = get_feature_func(img_dst_d_cv2)
            G_dst_d_vec = np.concatenate([G_l.flatten() for G_l in G_dst_d])

            Cost_this = calc_cost_func(G_ref, G_dst_d)

            ## get elapsed time
            t_render_elapsed  += t_render
            t_imageio_elapsed += t_imageio
            t_feature_elapsed += t_feature

            ## show information on the image
            img_text = "Cost: {0}\nParameter #{1:02d}".format(Cost_this, ind_param+1)
            Misc.show_text_on_image_cv2(img_dst_d_cv2, img_text, "find_step")

            ## accumulate to matrix A
            Gram_mat_diff = (G_dst_d_vec - G_dst_vec).reshape(-1)
            A[:, ind_param] = Gram_mat_diff / increment ## original
            ind_param += 1

            ## show the progress bar (1)
            prog = num_iter * (num_params + max_step) + ind_param
            cmds.progressWindow(edit=True, progress=prog)
            if cmds.progressWindow(query=1, isCancelled=1):
                success = False
                raise StopIteration

        if success==False: break ## [CHECK ABORT]

        ############################################################
        ## 2) get the gradient descent direction by linear algebra
        ############################################################
        At = np.transpose(A) # At = (15 x N)
        b = ( G_ref_vec - G_dst_vec ).reshape(-1)  # (N x 1), DESCENT direction (feature space)
        Atb = np.dot(At, b) # (15 x N ) x (N x 1) = (15 x 1), DESCENT direction (parameter space)

        AtA = np.dot(At, A)  # At x A = (15 x N) x (N x 15) = (15 x 15)
        try:
            AtA_inv = np.linalg.inv(AtA) #  ( 15 x 15 )
        except Exception as e:
            ## abort optimization (e.g. ESC key to abort)
            dump_file = folder_path + "/AtA_iter{0}.txt".format(num_iter)
            np.savetxt(dump_file, AtA)
            traceback.print_exc()
            success = False ## [ABORT]
            break
        x = np.dot( AtA_inv, Atb )

        Res_this = calc_cost_func(np.dot(A,x), b)

        ############################################################
        ## 3) compute GRADIENT direction
        ############################################################
        
        ## 3-i) STEEPEST GRADIENT (direction only)
        '''
        w = Atb / np.max(np.abs(Atb))
        beta = np.linalg.norm( b ) / np.linalg.norm( np.dot( A, w ) )
        '''

        ## 3-ii) consider the length (?) project solution x to get direction w
        #'''
        beta = np.max(np.abs(x))
        w = x / beta
        #'''

        ############################################################
        ## 4) determine alpha (=step size) to the next step
        ############################################################
        global step
        step = 0
        def SearchStep(alpha):
            global step, success

            global t_render_elapsed
            global t_imageio_elapsed
            global t_feature_elapsed

            ## compute parameter from alpha
            params01_vec = params01_vec_dst + alpha * w
            params01_vec = np.clip(params01_vec, 0.0, 1.0)
            params_dict  = convert_param_func(params01_vec)
            
            ############################################################
            ## current parameter image
            ############################################################
            path_dst_step = '{0}/step/iter_{1:04d}_{2:02d}'.format(folder_path, num_iter, step)
            img_dst_step_cv2, t_render, t_imageio = render_and_load(params_dict, path_dst_step)
            G_dst_step, t_feature = get_feature_func(img_dst_step_cv2)

            Cost_step = calc_cost_func(G_ref, G_dst_step)

            ########################################
            ## get elapsed time
            ########################################
            t_render_elapsed  += t_render
            t_imageio_elapsed += t_imageio
            t_feature_elapsed += t_feature

            ## show information on the image
            img_text = "Cost: {0}\n#iter {1}, residual = {2}, #step {3}".format(Cost_step, num_iter, Res_this, step)
            Misc.show_text_on_image_cv2(img_dst_step_cv2, img_text, "find_step")

            ## show the progress bar (2)
            prog = num_iter * (num_params + max_step) + num_params + step
            cmds.progressWindow(edit=True, progress=prog)
            if cmds.progressWindow(query=1, isCancelled=1):
                success = False ## [ABORT]
                raise StopIteration

            step += 1
            return Cost_step

        opt = optimize.minimize_scalar(SearchStep, bounds=(0.0, beta), method='bounded', options={'maxiter':max_step})

        if success==False: break ## [CHECK ABORT]

        ## abort the iteration when there was no improvement neither Cost nor Residual.
        Cost_this = opt.fun
        if Cost_prev < Cost_this and Res_prev < Res_this:
            break
        
        ## proceed to the next step
        Res_prev = Res_this
        alpha = opt.x
        params01_vec_dst = alpha * w + params01_vec_dst
        params01_vec_dst = np.clip(params01_vec_dst, 0.0, 1.0)
    
    ## best parameter until the last iteration ...
    best_params_dict = convert_param_func(params_01_vec_best)
    
    cmds.progressWindow(endProgress=1)
    return success, best_params_dict


###############################################################################
## example of usage
###############################################################################
if "__main__" == __name__:

    ############################################################
    ## user-specified values & paths
    ############################################################
    imgFileExt = "jpg"
    folder_reference = "C:/FurImages/Experiment1-CGSamples/_References_960x540"
    folder_temp_root = "C:/FurImages/Experiment1-CGSamples"
    num_of_repeat = 1

    ########################################
    ## parameter normalization [0.0:1.0]
    ########################################
    def convert_param_func(params01_vec):
        params01_dict = {}
        for cnt, key in enumerate(FurParam.ParamsGeom):
            params01_dict[key] = params01_vec[cnt]

        params_dict = FurParam.ConvertFurParams(params01_dict, True)
        return params_dict

    ## pick reference image files from folder
    fileList = next(os.walk(folder_reference))[2]
    fileList = [imgFile for imgFile in fileList if ".{0}".format(imgFileExt)==os.path.splitext(imgFile)[1]]
    
    ############################################################
    ## iteration:
    ############################################################
    abort = False

    for i in range(num_of_repeat):
        for imgFile in fileList:

            ## initialize renderer wrapper
            furRenderer = Misc.FurRenderer()

            ############################################################
            ## create temporary folder and copy image file to the folder
            ############################################################
            img_ref_path = "{0}/{1}".format(folder_reference, imgFile)

            folder_root = "{0}/{1}_{2}".format(
                folder_temp_root,
                os.path.splitext(imgFile)[0],
                datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            os.makedirs(folder_root) # root folder to preserve optimization progress
            shutil.copy2(img_ref_path, folder_root+"/_ref_image.{0}".format(imgFileExt))

            furRenderer.Init(folder_root)

            ############################################################
            ## get default colors for initialization
            ############################################################
            init_params_dict = FurParam.ParamsColor

            ## get .csv if exists
            csv_ref_path = os.path.splitext(img_ref_path)[0]+".csv"
            if True==os.path.isfile(csv_ref_path):
                shutil.copy2(csv_ref_path, folder_root+"/_ref_image.csv")

                ## read .csv and add to init_params_dict
                init_params_dict_file = FurParam.csv2dict(csv_ref_path)

                from collections import OrderedDict
                init_params_dict = OrderedDict( 
                    list(init_params_dict.items()) +
                    list(init_params_dict_file.items())
                )
            
            ## assign the initial color parameters before optimization
            furRenderer.RenderFur(init_params_dict, folder_root+"/temp")
            
            ############################################################
            ## invert initial parameter dictionary as vector
            ############################################################

            print(img_ref_path)

            ## 1) random initial parameters [NOT SO USEFUL]
            #params01_vec_dst = np.random.random(15)

            ## 2) use initial parameters from Bayesian optimization
            #'''
            csv_ref_path = os.path.splitext(img_ref_path)[0]+"_bayesopt.csv"
            init_params_dict = FurParam.csv2dict(csv_ref_path)
            params01_vec_dst = []
            #'''

            for key in FurParam.ParamsGeom:
                value = init_params_dict[key]
                val01 = FurParam.ConvertFurParam(key, value)
                params01_vec_dst.append(val01)

            ############################################################
            ## enter optimization routine
            ############################################################

            ## initialize elapsed time for each component as 0:00:00.000
            global t_render_elapsed
            global t_imageio_elapsed
            global t_feature_elapsed
            t_render_elapsed  = datetime.min - datetime.min
            t_imageio_elapsed = datetime.min - datetime.min
            t_feature_elapsed = datetime.min - datetime.min
            t_total_start = datetime.now()

            ## run optimization on GEOMETRY parameters
            succeeded, shape_param_dict = GradientDescent(
                vgg_max_gray_gram, calc_cost_func, furRenderer.RenderFur,
                convert_param_func, params01_vec_dst,
                folder_root, imgFileExt
            )
            
            ## export elapsed time for each component
            t_total_end     = datetime.now()
            t_total_elapsed = t_total_end - t_total_start
            t_etc_elapsed   = t_total_elapsed - (t_render_elapsed+t_imageio_elapsed+t_feature_elapsed)
            
            with open(folder_root+"/elapsed.txt", "w+") as txt:
                txt.write("elapsed time   = {0}\n".format(t_total_elapsed) )
                txt.write("rendering time = {0}\n".format(t_render_elapsed) )
                txt.write("imageio time   = {0}\n".format(t_imageio_elapsed) )
                txt.write("feature extraction time = {0}\n".format(t_feature_elapsed) )
                txt.write("et cetera time = {0}\n".format(t_etc_elapsed) )

            ## render the best result
            furRenderer.RenderFur(shape_param_dict, folder_root+"/_best_shape")
            
            if False==succeeded:
                abort = True
                break
        
        ## abort remained task
        if abort:
            break

    ############################################################
    ## 
    ############################################################
    cv2.destroyAllWindows()
