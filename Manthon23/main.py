from flask import Flask, render_template, redirect, jsonify, session, url_for, request,g
from datetime import datetime, timedelta
from functools import wraps
from markupsafe import Markup
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objs as go
import plotly.io as pio
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
import json
import recommendation
from recommendation import Computation

warnings.filterwarnings('ignore')
app = Flask(__name__, template_folder='my_templates')
app.secret_key = 'my_secret_key'

app.debug = True
global input_data
global input_data2
@app.before_first_request
def clear_session():
    session.pop('username', None)


@app.route('/')
def hello():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            # set the session variable to the username
            session['username'] = username
            return redirect(url_for('tabs'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        # display login form
        return render_template('login.html')

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/autocompleteProducts', methods=['GET'])
@login_required
def autocompleteProducts():
    # Load the CSV file into a Pandas dataframe
    df = pd.read_csv('data/SampleUsageData9March.csv')

    # Get the unique product names
    product_names = df['Product Name'].unique()
    print(product_names)
    search = request.args.get('search')
    suggestions = product_names;
    results = [suggestion for suggestion in suggestions if search.lower() in suggestion.lower()]
    return jsonify(results)


@app.route('/autocompleteCustomers')
@login_required
def autocompleteCustomers():
    # Load the CSV file into a Pandas dataframe
    df = pd.read_csv('data/SampleUsageData9March.csv')

    # Get the unique customer names
    customer_names = df['Customer Name'].unique()
    print(customer_names)
    search = request.args.get('search')
    suggestions = customer_names;
    results = [suggestion for suggestion in suggestions if search.lower() in suggestion.lower()]
    return jsonify(results)


@app.route('/usageComparison', methods=['GET'])
@login_required
def prdUsageComparison():
    numberOfDays = request.args.get('date')
    if numberOfDays == '' or numberOfDays == '0':
        numberOfDays = 365
    productName = request.args.get('productName')
    customerName = request.args.get('customerName')

    # Load the CSV file into a Pandas dataframe
    df = pd.read_csv('data/SampleUsageData9March.csv')

    df['Order Date Time'] = pd.to_datetime(df['Order Date Time'])
    date_threshold = datetime.now() - timedelta(days=int(numberOfDays))

    mask = (df['Order Date Time'] >= date_threshold)
    filtered_df = df.loc[mask]
    df = filtered_df
    filtered_data = filtered_df.to_dict(orient='records')

    if customerName is not None and customerName != '':
        input_data = str(customerName)
        input_data2 = 'Anesthesia Machine'

    if productName is not None and productName != '':
        input_data2 = str(productName)
        input_data = 'Kaiser Permanente'

    html_content = getGraphAndTable(df, input_data, input_data2, customerName, productName, 'true')
    return jsonify({'html': html_content})


@app.route('/tabs', methods=['GET'])
@login_required
def tabs():
    # Load the CSV file into a Pandas dataframe
    df = pd.read_csv('data/SampleUsageData9March.csv')

    # Get the unique customer names
    customer_names = df['Customer Name'].unique()

    # Get the unique product names
    product_names = df['Product Name'].unique()

    customerName = customer_names[0]
    productName = product_names[0]
    input_data = customerName
    input_data2 = productName

    html_fragment = getGraphAndTable(df, input_data, input_data2, customerName, productName, 'false')

    return html_fragment

def getGraphAndTable(df, input_data, input_data2, customerName, productName, isJsonRequest):
  
    computation_obj=Computation()

    computation_obj.computation(input_data,input_data2)
    corr_ = computation_obj.getcorr_heatmap()
    df_corr = pd.DataFrame(corr_)
    heatmap1 = go.Heatmap(z=df_corr.values.tolist(), x=df_corr.columns.tolist(), y=df_corr.index.tolist(),
                          colorscale='RdBu')

    # Define your layout here
    layout = go.Layout(
        title='Product Correlations with ISV Data Insights'
    )

    # Define your layout here
    layout2 = go.Layout(
        title='Product Correlations through Usage Patterns'
    )
    corr_2 = computation_obj.getcorr_heatmap_user()
    df_corr2 = pd.DataFrame(corr_2)
    heatmap2 = go.Heatmap(z=df_corr2.values.tolist(), x=df_corr2.columns.tolist(), y=df_corr2.index.tolist(),
                          colorscale='RdBu')
    # Create the figures
    fig = go.Figure(data=[heatmap1], layout=layout)
    fig2 = go.Figure(data=[heatmap2], layout=layout2)

 

    my_df = computation_obj.getproducts()
    my_df2 = computation_obj.getcustomers()

    table = my_df.to_html(classes='table table-striped')
    table2 = my_df2.to_html(classes='table table-striped')
    # Create the trace for each line
    trace1 = go.Scatter(x=my_df['Product Name'], y=my_df['Predicted Usage'], mode='lines', name='Predicted Usage')
    trace2 = go.Scatter(x=my_df['Product Name'], y=my_df['Actual Usage'], mode='lines', name='Actual Usage')

    # Create the layout
    layout1 = go.Layout(title='Usage Comparison', width=1350, xaxis=dict(title='Product Name'), yaxis=dict(title='Usage'))

    # Create the figure object and add the traces and layout
    fig_graph1 = go.Figure(data=[trace1, trace2], layout=layout1)

    trace1_cust = go.Scatter(x=my_df2['Customer Name'], y=my_df2['Predicted Usage'], mode='lines',
                             name='Predicted Usage')
    trace2_cust = go.Scatter(x=my_df2['Customer Name'], y=my_df2['ISV Predicted Usage'], mode='lines',
                             name='ISV Predicted Usage')
    trace3_cust = go.Scatter(x=my_df2['Customer Name'], y=my_df2['Actual Usage'], mode='lines', name='Actual Usage')

    # Create the layout
    layout2 = go.Layout(title='Usage Comparison', width=1350, xaxis=dict(title='Customer Name'), yaxis=dict(title='Usage'))

    # Create the figure object and add the traces and layout
    fig_graph2 = go.Figure(data=[trace1_cust, trace2_cust, trace3_cust], layout=layout2)

    if isJsonRequest == 'true':
        # Generate the HTML content for the <div> element
        if customerName is not None and customerName != '':
            fig_json = pio.to_json(fig_graph1)
            table = table
            plot_graph = f'<div id="plot_graph1">{fig_json}</div>'
            html_content = f'<div id="plot_graphCustomerNameJson">{Markup(plot_graph)}</div><table>{Markup(table)}</table>'
        else:
            fig_json = pio.to_json(fig_graph2)
            table = table2
            plot_graph = f'<div id="plot_graph2">{fig_json}</div>'
            html_content = f'<div id="plot_graphPrdNameJson">{Markup(plot_graph)}</div><table>{Markup(table)}</table>'
        return html_content
    else:
        html_fragment = render_template('tabs.html', plot=fig.to_html(full_html=False), plot2=fig2.to_html(full_html=False),
                                    plot_graph2=fig_graph2.to_html(full_html=True),
                                    plot_graph1=fig_graph1.to_html(full_html=True), customerName=customerName,
                                    productName=productName, table=table, table2=table2)
        return html_fragment

class DataRecords:
    def __init__(self, plot_graph2, plot_graph1, table, table2):
        self.plot_graph2 = plot_graph2
        self.plot_graph1 = plot_graph1
        self.table = table
        self.table2 = table2

if __name__ == "__main__":
    app.run(host='0.0.0.0')
