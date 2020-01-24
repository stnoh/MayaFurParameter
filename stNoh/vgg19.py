import numpy as np
import keras
from keras import backend as K

###############################################################################
## VGG-19 network
###############################################################################
def VGG19(input_tensor=None, input_shape=None, avgPooling=False):
    """
    Creates VGG19 structure and loads weights of pretrained data.
    """

    # input shape: if it is not specified, then undefined size with 3 channels
    if input_shape==None:
        data_format = K.image_data_format()
        if data_format not in {'channels_first', 'channels_last'}:
            raise ValueError('Invalid data_format:', data_format)

        input_shape = (None, None, 3) if data_format=='channels_last' else (3, None, None)

    ############################################################
    # define input layer
    ############################################################
    from keras.layers import Input, Conv2D
    
    if input_tensor is None:
        img_input = Input(shape=input_shape)
    else:
        if not K.is_keras_tensor(input_tensor):
            img_input = Input(tensor=input_tensor, shape=input_shape)
        else:
            img_input = input_tensor

    ############################################################
    # construct VGG19 structure
    ############################################################
    from keras.layers import MaxPooling2D     # Default VGG
    from keras.layers import AveragePooling2D # Following [Gatys15]

    # Block 1
    x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv1')(img_input)
    x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv2')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(x) if avgPooling is False else AveragePooling2D((2, 2), strides=(2, 2), name='block1_pool')(x)
    
    # Block 2
    x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv1')(x)
    x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv2')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(x) if avgPooling is False else AveragePooling2D((2, 2), strides=(2, 2), name='block2_pool')(x)
    
    # Block 3
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv1')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv2')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv3')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv4')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(x) if avgPooling is False else AveragePooling2D((2, 2), strides=(2, 2), name='block3_pool')(x)
    
    # Block 4
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv1')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv2')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv3')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv4')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(x) if avgPooling is False else AveragePooling2D((2, 2), strides=(2, 2), name='block4_pool')(x)
    
    # Block 5
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv1')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv2')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv3')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv4')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(x) if avgPooling is False else AveragePooling2D((2, 2), strides=(2, 2), name='block5_pool')(x)

    # Create model (no top)
    from keras.models import Model
    model = Model(img_input, x, name='vgg19')

    # load weights: if it is the first time, then download from url ...
    WEIGHTS_PATH = ('https://bitbucket.org/stnoh/Maya-PythonPackages/'
                    'raw/master/'
                    'models/vgg19_weights_normalized.h5')
    weights_path = keras.utils.get_file(
        'vgg19_weights_normalized.h5',
        WEIGHTS_PATH,
        cache_subdir='models',
        file_hash='27ece8fbdcc9ca117b0f8aea2839c30e')
    model.load_weights(weights_path)

    return model


###############################################################################
# conversion between image library (cv2) and keras
###############################################################################
imagenet_mean = (103.939, 116.779, 123.68) ## BGR [0.0:255.0]

def preprocess_input(img_BGR_uint8):
    """
    Converts image format from CV2 (uint8, BGR) to keras (float 0.0:255.0, BGR)
    """

    # (int) [0,255] -> [0.0:255.0] (float)
    img_BGR_float = img_BGR_uint8.astype('float32')

    # subtract imagenet mean (BGR order)
    img_BGR_float[:,:,0] -= imagenet_mean[0]
    img_BGR_float[:,:,1] -= imagenet_mean[1]
    img_BGR_float[:,:,2] -= imagenet_mean[2]

    # check tensor format
    data_format = K.image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Invalid data_format:', data_format)
    
    # synchronize tensor format
    # cv2 [HWC] -> [CHW] keras (channels_first)
    if data_format == 'channels_first':
        img_BGR_float = img_BGR_float.transpose(2,0,1)

    # extend as tensor [1,H,W,C] (or [1,C,H,W])
    img_keras = np.expand_dims(img_BGR_float, axis=0)
    return img_keras


###############################################################################
# compute gram matrix (in numpy/keras)
###############################################################################
def np_gram_matrix(x):
    """
    Computes gram matrix from activations, defined as np array.
    """

    ## change to 'channels_first' and make flat
    if K.image_data_format() == 'channels_first':
        F = x[:]
    else:
        F = np.transpose(x[:], (2, 0, 1))
    F = F.reshape(F.shape[0], -1)

    # N feature maps, M vectorized pixels
    N = F.shape[0]
    M = F.shape[1]

    ## construct gram matrix
    G = np.dot(F, F.T) / (2. * N * M)
    return G

def keras_gram_matrix(x):
    """
    Computes gram matrix from activations in keras platform.
    """
    assert K.ndim(x) == 3 # suppose a single image

    ## change to 'channels_first' and make flat
    if K.image_data_format() == 'channels_first':
        F = K.batch_flatten(x)
    else:
        F = K.batch_flatten(K.permute_dimensions(x, (2, 0, 1)))

    # N feature maps, M vectorized pixels
    N = int(F.shape[0])
    M = int(F.shape[1])

    ## construct gram matrix
    G = K.dot(F, K.transpose(F)) / (2. * N * M)
    return G
