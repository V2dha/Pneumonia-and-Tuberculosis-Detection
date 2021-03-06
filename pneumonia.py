# -*- coding: utf-8 -*-
"""Pneumonia.ipynb

Automatically generated by Colaboratory.

"""

!pip install kaggle

!mkdir .kaggle

#Token and User Id hidden

!cp /content/.kaggle/kaggle.json ~/.kaggle/kaggle.json

!kaggle config set -n path -v{/content}

!chmod 600 /root/.kaggle/kaggle.json

!kaggle datasets download -d paultimothymooney/chest-xray-pneumonia -p /content

!unzip chest-xray-pneumonia.zip

!ls chest_xray/test

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import cv2
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
import keras
from keras import layers
from keras.models import Sequential
from keras.layers import Input,Dense,Conv2D,Activation,AveragePooling2D,BatchNormalization,MaxPooling2D,Dropout,Flatten
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
from keras.callbacks import ReduceLROnPlateau
import seaborn as sn
from keras.utils import plot_model
from sklearn.metrics import confusion_matrix,classification_report



from keras.models import Model

from keras.callbacks import ReduceLROnPlateau,EarlyStopping

train = ImageDataGenerator(rescale=1./255, zoom_range=0.3)
val = ImageDataGenerator(rescale=1./255)

train_data = train.flow_from_directory('chest_xray/chest_xray/train',target_size=(224,224),batch_size=32,class_mode='binary',shuffle=True)

val_data = val.flow_from_directory('chest_xray/chest_xray/test',target_size=(224,224),batch_size=32,class_mode='binary',shuffle=True)

test_data = val.flow_from_directory('chest_xray/chest_xray/test',target_size=(224,224),batch_size=1,class_mode='binary',shuffle=False)

img_in = Input((224,224,3))

x = Conv2D(filters=16, kernel_size=(3, 3), activation='relu', padding='same')(img_in)
x = Conv2D(filters=16, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = BatchNormalization()(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = BatchNormalization()(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = BatchNormalization()(x)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Dropout(rate=0.2)(x)

x = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same')(x)
x = BatchNormalization()(x)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Dropout(rate=0.2)(x)

x = Flatten()(x)
x = Dense(units=512, activation='relu')(x)
x = Dropout(rate=0.7)(x)
x = Dense(units=128, activation='relu')(x)
x = Dropout(rate=0.5)(x)
x = Dense(units=64, activation='relu')(x)
x = Dropout(rate=0.3)(x)
output = Dense(units=1, activation='sigmoid')(x)

model = Model(inputs=img_in, outputs=output)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

lr_reduce = ReduceLROnPlateau(monitor='val_loss', factor=0.4, patience=2, verbose=2, mode='max')
early_stop = EarlyStopping(monitor='val_loss', min_delta=0.1, patience=1, mode='min')

model.load_weights('model.h5')

hist = model.fit_generator(train_data, steps_per_epoch=train_data.samples // 32, epochs=10, validation_data=val_data, validation_steps=val_data.samples // 32, callbacks=[lr_reduce])

!pip install livelossplot

from keras.utils import plot_model

plot_model(model,show_layer_names=False,show_shapes = True,dpi = 128)

preds = model.predict_generator(test_data)

model

preds = np.round(preds)

model.evaluate_generator(test_data)

print(classification_report(test_data.classes,preds))

model.save_weights('model.h5')

cm = confusion_matrix(test_data.classes,preds)

sn.set(font_scale = 2.5)
plt.figure(figsize = (11,8))
hm = sn.heatmap(cm,cmap = 'Blues_r',annot = True,xticklabels = ['Normal','Pneumonia'],yticklabels = ['Normal','Pneumonia'],annot_kws={"size": 20})
hm.set_yticklabels(rotation = 0,labels = hm.get_yticklabels())

plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.legend(['train','test'])
plt.title('loss_descend')

plt.plot(hist.history['acc'])
plt.plot(hist.history['val_acc'])
plt.legend(['train','test'])
plt.title('accuracy')

model.summary()

probs = model.predict_generator(test_data)

from sklearn.metrics import roc_auc_score,roc_curve

print(roc_auc_score(test_data.classes,probs))

fpr,tpr,_ = roc_curve(test_data.classes,probs)

plt.figure(figsize = (11,8))
plt.plot(fpr,tpr,label = 'Pneumonia Prediction')
plt.plot([0,1],[0,1],'r--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC-AUC Curve')
plt.legend(loc = 4)

plot_model(model)

