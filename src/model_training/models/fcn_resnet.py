"""
ResNet based FCN.
"""
from keras.models import Model
from keras.layers import (Input,
                          Activation,
                          Convolution2D,
                          Reshape,
                          Lambda,
                          merge)
import tensorflow as tf

from .resnet import ResNet


def make_fcn_resnet(input_shape, nb_labels, drop_prob):
    input_shape = tuple(input_shape)
    nb_rows, nb_cols, _ = input_shape
    nb_labels = nb_labels

    input_tensor = Input(shape=input_shape)
    model = ResNet(input_tensor=input_tensor, drop_prob=drop_prob)
    print(model.summary())
    def resize_bilinear(images):
        return tf.image.resize_bilinear(images, [nb_rows, nb_cols])

    x32 = model.get_layer('activation3d').output
    x16 = model.get_layer('activation4f').output
    x8 = model.get_layer('activation5c').output

    c32 = Convolution2D(nb_labels, 1, 1, name='conv_labels_32')(x32)
    c16 = Convolution2D(nb_labels, 1, 1, name='conv_labels_16')(x16)
    c8 = Convolution2D(nb_labels, 1, 1, name='conv_labels_8')(x8)

    r32 = Lambda(resize_bilinear, name='resize_labels_32')(c32)
    r16 = Lambda(resize_bilinear, name='resize_labels_16')(c16)
    r8 = Lambda(resize_bilinear, name='resize_labels_8')(c8)

    m = merge([r32, r16, r8], mode='sum', name='merge_labels')

    x = Reshape((nb_rows * nb_cols, nb_labels))(m)
    x = Activation('softmax')(x)
    x = Reshape((nb_rows, nb_cols, nb_labels))(x)

    model = Model(input=input_tensor, output=x)

    return model
