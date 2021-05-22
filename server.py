import os
import sys
import shutil
import pickle 
import numpy as np
from flask import Flask, jsonify, abort, request, make_response,\
                    url_for,redirect, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename

from feature_extractor import get_feature

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app = Flask(__name__, static_url_path = "")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auth = HTTPBasicAuth()


def load_features(feature_path):
    features = pickle.load(open(feature_path, 'rb'))
    image_paths = list(features.keys())
    features = list(features.values())
    features = np.array(features)
    return image_paths, features

feature_path = 'static/features.pickle'
image_paths, features = load_features(feature_path)

def recommend(image_path, img_dir='dataset', k=9, save_dir='static/result'):
    os.makedirs(save_dir, exist_ok=True)
    # print(image_path)
    feature = get_feature(image_path)
    dists = np.linalg.norm(features-feature, axis=1)
    ids = np.argsort(dists).tolist()
    for i, id in enumerate(ids):
        img_path, score = image_paths[id], dists[id]
        save_path = os.path.join(save_dir, img_path.split('/')[-1])
        if os.path.exists(img_path):
            shutil.copyfile(src=img_path, dst=save_path)
        if i+1 == k:
            return
    return

@app.route('/imgUpload', methods=['GET', 'POST'])
def upload():
    result = 'static/result'
    if os.path.exists(result):
        shutil.rmtree(result)
    if request.method == 'POST' or request.method == 'GET':
        print(request.method)
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and file.filename[-3:] in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            inputloc = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            recommend(inputloc, save_dir=result)

            images = {'image'+str(i):'result/'+image_name for i, image_name in enumerate(os.listdir(result))}
            # print(images)

            return jsonify(images)

@app.route("/")
def main():
    
    return render_template("main.html")   
if __name__ == '__main__':
    app.run(debug=False, threaded=False)