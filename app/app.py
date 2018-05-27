from flask import Flask
from flask import render_template
import numpy as np
import pandas as pd
import json
import pickle
import plotly
from plotly.offline import plot
from plotly import tools
import plotly.graph_objs as go

application = Flask(__name__)


@application.route("/")
def overview():
    return render_template('index.html') 

@application.route("/why1")

def reason():

	df = pd.read_pickle("line_chart.pkl")

	def line_plot(day, machine, home):
    
	    # select machine
	    df_Machine = df[['Day', 'Time', 'Home', machine]]
	    
	    # gropuby by day, home, time of day
	    df_Machine = df_Machine.groupby(['Day', 'Home', 'Time'], as_index=False).mean()
	    
	    # Select day
	    df_Machine_Day = df_Machine[df_Machine['Day'] == day]
	    
	    
	    # Select data for the customer
	    customer = df_Machine_Day[df_Machine_Day['Home'] == home]
	    
	    #Select data for others
	    others = df_Machine_Day[df_Machine_Day['Home'] != home]
	    others_mean_std = others[['Day', 'Time', machine]].groupby(['Day', 'Time'], as_index=False).agg({'mean', 'std'})
	    others_mean = others_mean_std[machine]['mean'].reset_index()['mean']
	    others_std = others_mean_std[machine]['std'].reset_index()['std']
	    others_time = others_mean_std.reset_index()['Time']

	    trace1 = go.Scatter(
	        x = customer['Time'],
	        y = customer[machine],
	        name = 'Home '+str(home),
	        line = dict(
	            color = ('rgb(69,117,180)'),
	            width = 3)
	    )
	    
	    
	    trace2 = go.Scatter(
	        x = others_time,
	        y = others_mean,
	        name = 'average use of other homes',
	        line = dict(
	            color = ('rgb(161,215,106)'),
	            width = 3,
	            dash = 'dot')
	    )
	    
	    trace3 = go.Scatter(
	        x = others_time,
	        y = others_mean + others_std,
	        name = 'Upper Limit',
	        line = dict(
	            color = ('rgb(263,163,201)'),
	            width = 4,
	            dash = 'dash')
	    )
	       
	    trace4 = go.Scatter(
	        x = others_time,
	        y = others_mean - others_std,
	        name = 'Lower Limit',
	        line = dict(
	            color = ('rgb(263,163,201)'),
	            width = 4,
	            dash = 'dash')
	    )
	        
	    data = [trace1, trace2, trace3, trace4]
	    
	    
	    layout = go.Layout(yaxis=dict(title='Usage energy'),
	                   xaxis=dict(title='Time')
	                  )
	    
	    fig = go.Figure(data=data, layout=layout)
	    
	    return (fig)

	plotly_graph = line_plot('Wednesday', 'DW', 2)
	plotly_graph1 = line_plot('Wednesday', 'WM', 2)

	graphJSON1 = json.dumps(plotly_graph, cls=plotly.utils.PlotlyJSONEncoder)
	graphJSON2 = json.dumps(plotly_graph1, cls=plotly.utils.PlotlyJSONEncoder)


	# Grid Image
	
	def create_total_bench(df, house=1, element='con'):

	    df_pv = df.groupby(['DateTime'], as_index=False).agg({'SI':['sum','std']})
	    df_pv = df_pv.iloc[0:672]
	    df_pv['max_lim'] = np.max(df_pv['SI']['sum'])	    
	    df_pv['solar_d'] = df_pv['SI']['sum'] - 10000

	    # create the graph for energy generation from solar panels
	    upper_bound = go.Scatter(
	        name='Max-Min capacity',
	        x=df_pv['DateTime'],
	        y=df_pv['max_lim']*1.1,
	        mode='lines',
	        line=dict(color = ('rgb(215,25,28)'),
	        width = 2,
	        dash = 'dash')
	    )
	    
	    da_1 = go.Scatter(
	        name='Discount Area',
	        x=df_pv['DateTime'],
	        y=df_pv['max_lim']*0.5,
	        mode='lines',
	        line=dict(color = ('rgb(26,150,65)'),
	        width = 2,
	        dash = 'dash')
	    )
	    
	    trace = go.Scatter(
	        name='Active Power of the Station',
	        x=df_pv['DateTime'],
	        y=df_pv['SI']['sum'],
	        mode='lines',
	        line=dict(color='rgb(31, 119, 180)')
	        
	    )
	    
	    da_4 = go.Scatter(
	        name='Discount Area 1',
	        x=df_pv['DateTime'],
	        y=df_pv['max_lim']*- 0.5,
	        mode='lines',
	        line=dict(color = ('rgb(26,150,65)'),
	        width = 2,
	        dash = 'dash'),
	        showlegend = False
	    )

	    lower_bound = go.Scatter(
	        name='Min capacity',
	        x=df_pv['DateTime'],
	        y=df_pv['max_lim']*-1.1,
	        line=dict(color = ('rgb(215,25,28)'),
	        width = 2,
	        dash = 'dash'),
	        showlegend = False
	    )
	    
	    pv_sce = go.Scatter(
	        name='Scenario 1',
	        x=df_pv['DateTime'],
	        y=df_pv['solar_d'],
	        line=dict(color = ('rgb(253,174,97)'),
	        width = 2,
	        dash = 'dash'),
	        showlegend = False
	    )
	    # -------------------------------------------------------------------
	    
	    # with continuous error bars
	    data = [upper_bound, trace, lower_bound, da_1 , da_4, pv_sce]

	    
	    layout = go.Layout(
	    yaxis=dict(title='Watts'),
	    title='Local Grid Performance',
	    showlegend = True)

	    fig = go.Figure(data=data, layout=layout)
	    return fig
	
	plot_grid = create_total_bench(df.copy(), element='con')

	graphJSON_grid = json.dumps(plot_grid, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('why1.html', graph_li=graphJSON1, graph_li1=graphJSON2, graphJSON_grid=graphJSON_grid)

@application.route("/why")
def why():
    return render_template('why2.html')
 
if __name__ == "__main__":
    application.run()