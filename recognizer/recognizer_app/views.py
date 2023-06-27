import os
import io
import json
from pathlib import Path

import gdown
from PIL import Image
from django.shortcuts import render, redirect

from django.http import JsonResponse
from .forms import AnalyzeForm
from django.conf import settings
import numpy as np
from .models import Image as ImageModel
from django.core.exceptions import ObjectDoesNotExist
import tensorflow as tf
from tensorflow.keras.models import load_model
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


# Create your views here.
def main(request):
    return render(request, 'recognizer_app/index.html', {})




# Global variable to store the loaded model
loaded_model = None

# https://drive.google.com/file/d/1MhlLfp43zOLiLnuFzBu3x7d6fIrh7iT5/view?usp=drive_link

def load_custom_model():
    # return 0
    global loaded_model
    if loaded_model is None:
        print('Loading the model ... ')

        url = 'https://drive.google.com/file/d/1MhlLfp43zOLiLnuFzBu3x7d6fIrh7iT5/view?usp=drive_link'

        # For docker
        output = 'recognizer/recognizer_app/src/Xception_tuned.h5'
        # For local
        # output = 'recognizer_app/src/Xception_tuned.h5'
        gdown.download(url, output, quiet=False, fuzzy=True)
        # For docker
        model_path = 'recognizer/recognizer_app/src/Xception_tuned.h5'
        # For local
        # model_path = 'recognizer_app/src/Xception_tuned.h5'
        # loaded_model = load_model(model_path)
        loaded_model = tf.keras.models.load_model(model_path, compile=False)
        # Get the last layer of the model
        last_layer = loaded_model.layers[-1]
        print(loaded_model)

        # Turn off the activation function of the last layer
        last_layer.activation = None
# Call the function to load the model
load_custom_model()


def classify(image=None):
    # return " uncomment view to  classify", " 0%"


    if not image:
        print("not image")
        return None

    # image_extensions = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.pbm', '.pgm', '.ppm',
    #                     '.pnm', '.ico', '.hdr', '.exr', '.svg']

    class_labels = ['Airplane', 'Automobile', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']

    try:
        img = image.convert('RGB')
        # img = img.resize((32, 32))

        img = np.array(img)
        img = np.expand_dims(img, axis=0)  # Add a batch dimension
        clean_predictions = loaded_model.predict(img)
    except Exception as err:
        print(err)
        img = image.convert('RGB')
        img = img.resize((32, 32))

        img = np.array(img)
        img = np.expand_dims(img, axis=0)  # Add a batch dimension
        clean_predictions = loaded_model.predict(img)

    # param_0 = np.array([1.40587545, 1.62797348, 1.44222336, 1.16518291, 1.194156, 1.22925031, 1.24019506, 1.17266833,
    #                     1.34761374, 1.47093253])
    #
    # param_1 = np.array([3.6108333, 3.55082633, 2.67590434, 2.71279497, 3.53879867, 3.3827658, 2.78051644, 3.74128725,
    #                     3.69832112, 4.93112212])

    param_0 = np.array([1.350902798343926,1.604098186688871,1.487372586762944,1.4245593114217021,1.11647063138921,
                        1.1752968166724223,1.3050880249428543,1.1973399379334915,1.275995021357589,1.3561731873792415])

    param_1 = np.array([2.0131649192509293,2.2933596623960817,1.1635691730345663,0.9178184385723627,1.5868513101998958,
                        1.564265064911758,1.0412018766923974,1.8628664506696946,2.0594879005495135,3.391081867066545])
    def custom_sigmoid(x, a, b):
        return 1.0 / (1 + np.exp(-a * (x - b)))

    sigmoid_predictions = custom_sigmoid(clean_predictions, param_0, param_1)
    sorted_indices = np.argsort(-sigmoid_predictions)[0][:10]
    # print(sigmoid_predictions[0])
    # print(sigmoid_predictions[0][sorted_indices])
    # print(sorted_indices)
    result_list = []
    result_str = ""
    for i in sorted_indices:
        if sigmoid_predictions[0][i] > 0.01:
            result_list.append(f"{class_labels[i]}: " +
                               f"{str(int(sigmoid_predictions[0][i] * 10000) / 100.0)}" + "%")
    if len(result_list) == 0:
        result_str = "Sorry, I can't classify your image.\n Maybe there are more than one object one the image"
    else:
        result_str = f"My prediction{'s are ' if len(result_list)>1 else ' is '} "+ ", ".join(result_list)

    #     if predictions[0][i] >= 0.05:
    #         result_str += class_labels[i] + ' - ' + str(int(predictions[0][i] * 10000) / 100.0) +'%, '
    # result_str = result_str[:-2]

    return result_str


    # predict_3 = sorted(sigmoid_predictions[0])[-5:]
    # index_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # dictionary = dict(zip(sigmoid_predictions[0], index_list))
    # predict_3_index = []
    # print(predict_3_index)
    # for i in predict_3:
    #     predict_3_index.append(dictionary.get(i, -1))
    # result_str = ''
    # for i in predict_3_index[::-1]:
    #
    #     if predictions[0][i] >= 0.05:
    #         result_str += class_labels[i] + ' - ' + str(int(predictions[0][i] * 10000) / 100.0) +'%, '
    # result_str = result_str[:-2]
    #
    #
    # prediction_label = np.argmax(predictions)
    # percentage = str(int(predictions[0][prediction_label] * 10000) / 100.0)
    # return class_labels[prediction_label], result_str
    # # return 'bird'



@login_required  # Requires the user to be authenticated
def analyze_view(request, image_id=-1):

    if not request.user.is_authenticated:
        # Redirect or return an appropriate response for unauthorized users
        return HttpResponseForbidden()

    # try:
    #     image = ImageModel.objects.get(id=image_id)
    # except ImageModel.DoesNotExist:
    #     # Handle the case when the image doesn't exist
    #     return redirect('/analyze/')
    #
    # if image.user != request.user:
    #     # Return a forbidden response if the image doesn't belong to the user
    #     return HttpResponseForbidden()

    user_images = ImageModel.objects.filter(user=request.user).order_by('-last_viewed')
    for i, image in enumerate(user_images):
        if i > 8:
            # Delete file from local storage
            if os.path.exists(image.image.path):
                os.remove(image.image.path)
                image.delete()


    image_url = None
    # image_class = None
    result_3 = None
    mess = None
    errors = None

    try:
        image = ImageModel.objects.get(id=image_id)
        image_url = image.image.url
        # print(image.image)
        # print(image.image.url)
        image_path = image.image.path
        # print(image_url)
        # image_class,  result_3 = classify(Image.open(image_path))
        result_3 = classify(Image.open(image_path))
        # print(image_class)
    except ObjectDoesNotExist as err:
        mess = ''
        print(err, mess)

        pass


    if request.method == 'POST':
        form = AnalyzeForm(request.POST, request.FILES)
        form_err = form.errors.as_json( escape_html = True)
        errors = json.loads(form_err)
                    # if form.is_valid():
            #     image = form.cleaned_data['image']
            #     new_image = ImageModel(user=request.user, image=image, title=image.name)
            #     new_image.save()
            #     return redirect(f'/analyze/{new_image.id}/')
            # mess = 'This file type is not supported. Try again.'
        if form.is_valid():
            image = form.cleaned_data['image']
            new_image = ImageModel(user=request.user, image=image, title=image.name)
            new_image.save()
            return redirect(f'/analyze/{new_image.id}/')
    else:
        form = AnalyzeForm()

    return render(request, 'recognizer_app/index.html', {'image_url': image_url,
                                                         # 'image_class': image_class,
                                                         'images': user_images,
                                                         'result_3': result_3,
                                                         'mess': mess,
                                                         'errors': errors,
                                                         })






@login_required  # Requires the user to be authenticated
def analyze_view_by_id(request, image_id):
    try:
        image = ImageModel.objects.get(id=image_id)
    except ImageModel.DoesNotExist:
        return redirect('/analyze/')
    if image.user != request.user:
        # return HttpResponseForbidden()
        return redirect('/analyze/')
    return analyze_view(request, image_id=image_id)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/analyze/')  # replace 'home' with your desired landing page
        else:
            error_message = 'Invalid login credentials'
            return render(request, 'recognizer_app/login.html', {'error_message': error_message})
    else:
        return render(request, 'recognizer_app/login.html')
        # return render(request, 'login.html')


def signup_view(request):

    # uncomment this in final version
    # if request.user.is_authenticated:
    #     return redirect('/')

    if request.method == 'POST':
        error_message = []
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in!')
            print("Form is valid")
            return redirect('/login/')
        else:
            print("Form is invalid")
            print(form.errors)  # Print form errors to the console
            # for field in form.errors:
            #     error_message[field] = form.errors[field].as_text()
    else:
        form = SignUpForm()
    return render(request, 'recognizer_app/signup.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('main')