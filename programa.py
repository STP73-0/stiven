from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from PIL import Image
import os
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'supersecretkey'  # Change this to a random secret key

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                width = int(request.form['width'])
                height = int(request.form['height'])
                img = Image.open(file_path)
                img = img.resize((width, height))
                resized_filename = f"resized_{filename}"
                resized_file_path = os.path.join(app.config['UPLOAD_FOLDER'], resized_filename)
                img.save(resized_file_path)
                os.remove(file_path)  # Clean up the original file
                return render_template('index.html', image_path=resized_filename)
            except Exception as e:
                flash(f'Error processing image: {e}')
                return redirect(request.url)
        else:
            flash('Allowed file types are png, jpg, jpeg, gif')
            return redirect(request.url)
    return render_template('index.html', image_path=None)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
