from flask import Flask, render_template, request, send_file, url_for
from earningsviz import *  # Import your existing graph code
import os
import uuid

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    img_url = None
    if request.method == 'POST':
        ticker = request.form.get('ticker').upper()
        img_path = create_img_from_ticker(ticker)  # Replace with actual function call

        # Generate a unique filename for the new image
        _, ext = os.path.splitext(img_path)
        new_filename = str(uuid.uuid4()) + ext

        # Move the file to static folder
        new_img_path = os.path.join("static", new_filename)
        os.rename(img_path, new_img_path)

        # Get URL for the new image
        img_url = url_for('static', filename=new_filename)
    
    return render_template('index.html', img_url=img_url)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=False)
