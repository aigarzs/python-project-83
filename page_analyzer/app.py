from flask import Flask
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get("/")
def get_index():
    return "Hello Site Analyzer!"
