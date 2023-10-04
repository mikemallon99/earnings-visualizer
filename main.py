from flask import Flask, render_template, request, send_file, url_for
from earningsviz import *  # Import your existing graph code
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    img_str = None
    if request.method == 'POST':
        ticker = request.form.get('ticker').upper()
        img_buf = create_img_from_ticker(ticker)  # Replace with actual function call

        # Convert bytes to base64 encoded string and create a Data URL
        img_str = "data:image/png;base64," + base64.b64encode(img_buf).decode()
    
    return render_template('index.html', img_url=img_str)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
