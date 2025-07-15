from flask import Flask, render_template, request
import requests
import joblib
import time
from groq import Groq
import os

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    q = request.form.get("q")
    # db
    return(render_template("main.html"))

@app.route("/deepseek",methods=["GET","POST"])
def deepseek():
    return(render_template("deepseek.html"))

@app.route("/deepseek_reply",methods=["GET","POST"])
def deepseek_reply():
    q = request.form.get("q") or ""
    # load model
    client = Groq()
    completion_ds = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    return(render_template("deepseek_reply.html",r=completion_ds.choices[0].message.content))

@app.route("/llama",methods=["GET","POST"])
def llama():
    return(render_template("llama.html"))

@app.route("/llama_reply",methods=["GET","POST"])
def llama_reply():
    q = request.form.get("q") or ""
    # load model
    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": q}]    
        )
    return(render_template("llama_reply.html",r=completion.choices[0].message.content))

@app.route("/telegram",methods=["GET","POST"])
def telegram():
    return(render_template("telegram.html"))

@app.route("/telegram_reply",methods=["GET","POST"])
def one_time_telegram():
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    BASE_URL = "https://api.telegram.org/bot{TOKEN}/"
    data = ""
    while not data:
        response = requests.get(BASE_URL + 'getUpdates')
        if response.status_code != 200:
            print("Error fetching updates:", response.status_code)
            return render_template("telegram.html", r="Error fetching updates")
        if 'result' not in response.json():
            print("No updates found")
            return render_template("telegram.html", r="No updates found")   
        data = response.json()['result']
        print(data)
        time.sleep(5)

    print(data)
    q = data[-1]['message']['text']
    print('Query:', q)
    chat_id = data[-1]['message']['chat']['id']
    print('Chat ID:', chat_id)

    # load model
    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": q}]    
        )
    r=completion.choices[0].message.content

    # send reply
    requests.post(BASE_URL + 'sendMessage', data={
        'chat_id': chat_id,
        'text': r
    })
    
    return(render_template("main.html"))

@app.route("/dbs",methods=["GET","POST"])
def dbs():
    return(render_template("dbs.html"))

@app.route("/prediction",methods=["GET","POST"])
def prediction():
    q = float(request.form.get("q"))
    # load model
    #model = joblib.load("dbs.jl")
    # make prediction
    #pred = model.predict([[q]])
    return(render_template("prediction.html",r=90.2285+(-50.60*q)))

if __name__ == "__main__":
    app.run()