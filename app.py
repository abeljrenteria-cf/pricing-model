# importing Flask and other modules
import pandas as pd
import json
import plotly
import plotly.express as px
import pricing_model
from flask import Flask, jsonify, request, render_template
from datetime import datetime

# Flask constructor
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def gfg():
    
    # getting input from HTML form
    start_date = datetime.strptime(request.form.get("start_date"), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form.get("end_date"), '%Y-%m-%d').date()
    product = request.form.get("product_type")
    cost_method = request.form.get("cost-type")
    category = request.form.get("brand_class")

    df = pricing_model.filter_data()
    predictions = pricing_model.pricing(df, start_date, end_date, product, cost_method, category)
    average_cpv = predictions['CPV'].mean()

    fig = px.line(predictions, x="Date", y="CPV")
    graph1JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("index.html", 
    var1=start_date, 
    var2=end_date, 
    var3=product, 
    var4=cost_method, 
    var5=category, 
    var6=round(average_cpv, 4), 
    graph1JSON=graph1JSON)

if __name__=='__main__':
    app.run(debug=True)
