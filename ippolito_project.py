# Load libraries
from dash import Dash, dcc, html, Input, Output
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly
import plotly.graph_objs as go
import re
import sys
import time

#-----------------------------------------------------

# Init vars
offline = True
if offline:
	url_vars = 'data/vars.tsv'
	url_abbr = 'data/state_abbr.csv'
	url_data1 = 'data/04456-0001-Data.tsv'
	imgPath = 'https://github.com/mmippolito/cuny_data608_final_project/raw/main/'
else:
	url_vars = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/vars.tsv'
	url_abbr = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/state_abbr.csv'
	url_data1 = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/04456-0001-Data.tsv'
	imgPath = 'https://github.com/mmippolito/cuny_data608_final_project/raw/main/'

# Set dash app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)

#-----------------------------------------------------

# Define function to read data from github
def load_data(url, sep):
	
	# Load data
	print('Loading data from github: ' + url)
	df = pd.read_csv(url, sep=sep)

	# Return dataframe
	return df

# Define function to populate dropdown list based on a category of variable
def populate_dd(cat, subcat):

	# Populate dropdown list based on category
	if subcat == '.':
		d = {dfvar[dfvar['cat'] == cat].iloc[x]['var']: dfvar[dfvar['cat'] == cat].iloc[x]['descr'] \
			for x in range(0, dfvar[dfvar['cat'] == cat].shape[0])}
	else:
		d = {dfvar[(dfvar['cat'] == cat) & (dfvar['subcat'] == subcat) & (dfvar['var'] != 'p_black_') & (dfvar['var'] != 'p_hisp_l')].iloc[x]['var']: \
			dfvar[(dfvar['cat'] == cat) & (dfvar['subcat'] == subcat) & (dfvar['var'] != 'p_black_') & (dfvar['var'] != 'p_hisp_l')].iloc[x]['descr'] \
			for x in range(0, dfvar[(dfvar['cat'] == cat) & (dfvar['subcat'] == subcat) & (dfvar['var'] != 'p_black_') & (dfvar['var'] != 'p_hisp_l')].shape[0])}
	return d

# General function to update graph, called from callback function
def update_gr_general(outcome_var, indep_var):

	if outcome_var is None or indep_var is None:
		print('returning empty dict')
		return {}

	# Find missing value [value]
	miss_outcome = dfvar[dfvar['var'] == outcome_var]['missing'].values[0]
	miss_indep = dfvar[dfvar['var'] == indep_var]['missing'].values[0]

	# Fetch data
	dfplot1 = df1[(df1[outcome_var] != miss_outcome) & (df1[indep_var] != miss_indep)]
	
	# Display plot
	if dfvar[dfvar['var'] == indep_var]['vartype'].values[0] == 'cat':
		#fig1 = px.box(dfplot1, x=indep_var, y=outcome_var, color='year', width=800, height=400)
		fig1 = px.box(dfplot1, x='year', y=outcome_var, color=indep_var, width=800, height=400, points='outliers', color_discrete_sequence=['burlywood', 'cadetblue'])
	else:
		fig1 = px.scatter(dfplot1, x=indep_var, y=outcome_var, color='year', width=800, height=400, color_continuous_scale='deep_r')
	fig1.update_xaxes(mirror=False, showline=True, ticks='outside', linecolor='black', gridcolor='lightgrey', title=dfvar[dfvar['var'] == indep_var]['descr'].values[0])
	fig1.update_yaxes(mirror=False, showline=True, ticks='outside', linecolor='black', gridcolor='lightgrey', title=dfvar[dfvar['var'] == outcome_var]['descr'].values[0])
	fig1.update_layout(title='', plot_bgcolor='white')

	# Return
	return fig1

#-----------------------------------------------------

# Load data
dfvar = load_data(url_vars, '\t')
dfabbr = load_data(url_abbr, ',')
df1_raw = load_data(url_data1, '\t')

# Merge state abbreviations
df1 = pd.merge(df1_raw, dfabbr, on='state_na', how='inner')

# Create dict for year slider
d_yr = {str(x): str(x) for x in df1['year'].unique()}

# Factorize
df1['tiss'] = np.where(df1['tiss']==0, 'no', np.where(df1['tiss']==1, 'yes', 'na'))
df1['tisviol'] = np.where(df1['tisviol']==0, 'no', np.where(df1['tisviol']==1, 'yes', 'na'))
df1['govern'] = np.where(df1['govern']==0, 'no', np.where(df1['govern']==1, 'yes', 'na'))
df1['pre_guid'] = np.where(df1['pre_guid']==0, 'no', np.where(df1['pre_guid']==1, 'yes', 'na'))
df1['pre_volg'] = np.where(df1['pre_volg']==0, 'no', np.where(df1['pre_volg']==1, 'yes', 'na'))
df1['pre_par'] = np.where(df1['pre_par']==0, 'no', np.where(df1['pre_par']==1, 'yes', 'na'))
df1['rec_sent'] = np.where(df1['rec_sent']==0, 'no', np.where(df1['rec_sent']==1, 'yes', 'na'))
df1['presum_s'] = np.where(df1['presum_s']==0, 'no', np.where(df1['presum_s']==1, 'yes', 'na'))
df1['pre_rec_'] = np.where(df1['pre_rec_']==0, 'no', np.where(df1['pre_rec_']==1, 'yes', 'na'))

# Set aggregated policy data - c('tiss', 'tisviol', 'pre_guid', 'pre_volg', 'pre_par', 'rec_sent', 'presum_s', 'pre_rec_')
df1.loc[:, 'policy_agg'] = np.where((df1['pre_guid']=='yes') | (df1['pre_volg']=='yes') | (df1['pre_par']=='yes') | \
	(df1['rec_sent']=='yes') | (df1['presum_s']=='yes') | (df1['pre_rec_']=='yes'), 'yes', 'no')

# Set aggregated tiss for violent offenders - m10_we1a==1 | m16_we2a==1 | m22_we3a==1 | m28_we4a==1 | m52_vi1a==1 | m58_vi2a==1
df1.loc[:, 'tisviol_agg'] = np.where((df1['m10_we1a']==1) | (df1['m16_we2a']==1) | (df1['m22_we3a']==1) | \
	(df1['m28_we4a']==1) | (df1['m52_vi1a']==1) | (df1['m58_vi2a']==1), 'yes', 'no')

#-----------------------------------------------------

# Set layout
app.layout = html.Div(
	[
		html.Table([

			############################
			# Title block & intro text
			############################
			html.Tr([
				html.Td([
					html.P('Truth-in-Sentencing:', style={'font-weight': 'bold', 'font-size': '32px', 'margin': '0', 'padding': '0'}),
					html.P('Is It Working?', style={'font-weight': 'bold', 'font-size': '36px', 'margin': '0', 'padding': '0'}),
					html.P('By: Michael Ippolito', style={'font-weight': 'bold', 'font-size': '18px', 'margin': '0', 'padding': '0', 'text-align': 'left'}),
					html.P('CUNY DATA608', style={'font-weight': 'bold', 'font-size': '14px', 'margin': '0', 'padding': '0', 'text-align': 'left'}),
					html.P('May 2023', style={'font-weight': 'bold', 'font-size': '14px', 'margin': '0', 'padding': '0', 'text-align': 'left'}),
					html.Br(),
					html.Img(src=imgPath + 'img_prison.jpg', height='420px'),
					html.Br(),
					html.Br(),
					html.P('An Uneven System', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
					html.P('Before the 1990s, many prisoners incarcerated in the US criminal justice system only served a fraction of their sentence, often being released for good behavior or other mitigating factors. These factors were applied unevenly at the discretion of parole boards. Public pressure led to the passage of the Violent Crime Control and Enforcement Act (VCCLEA) in 1994, which gave incentives to states that required prisoners to serve at least 85% of their sentence.', 
						style={'font-size': '14px', 'text-align': 'left'}
					),
				], style={'border': 'none', 'padding': '0px', 'text-align': 'center'}, colSpan=2),
			], style={'border': 'none'}),

			############################
			# State map - TISS
			############################
			html.Tr([
				html.Td([
					html.Label(id='lbl_map_title', children=['Truth-in-Sentencing Policies'])
				], style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=2),
			], style={'border': 'none', 'padding': '0px'}),
			html.Tr([
				html.Td([
					dcc.Graph(id='gr_map1')
				], style={'border': 'none', 'padding': '0px'}),
				html.Td([
					dcc.Graph(id='gr_map2')
				], style={'border': 'none', 'padding': '0px'})
			], style={'border': 'none', 'padding': '1px'}),
			html.Tr([
				html.Td([
					dcc.Graph(id='gr_map3')
				], style={'font-size': '14px', 'border': 'none', 'padding': '1px'}, colSpan=2),
			], style={'border': 'none', 'padding': '0px'}),
			html.Tr([
				html.Td([
					dcc.Slider(id='sl_year', min=1975, max=2002, step=3, value=1975, marks=d_yr, updatemode='drag')
					#html.Button(id='but_play', value='Play', n_clicks=0, disabled=False),
					#dcc.Interval(id="ani_map", disabled=True)
				], style={'border': 'none', 'padding': '1px', 'text-align': 'left'}, colSpan=2)
			], style={'border': 'none', 'padding': '1px'}),
			html.Tr([
				html.Td([
					html.Label([''])
				], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=2),
			], style={'border': 'none', 'padding': '0px'}),
			html.Tr([
				html.Td([
					html.Hr()
				], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=2)
			], style={'border': 'none', 'padding': '0px'}),
			html.Tr([
				html.Td([

						############################
						# TIS
						############################
						html.Tr([
							html.Td([
								html.Img(src=imgPath + 'img_tis.jpg', height='200px'),
								html.P('Is TIS working?', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
								html.P("Arguments leading to passage of the VCCEA included that truth in sentencing (TIS) laws would deter future criminal behavior, would render justice to the perpetrator for the crime commited, and that time served would theoretically be unbiased and no longer at the whim of a parole board. Opponents of TIS argue that TIS leads to prison overcrowding, that the cost of incarcerating prisoners longer could be better spent on crime prevention programs, that it disincentivizes good behavior, and that it in fact does not serve as a deterrent to future crime. Further, it leaves judges no room in weighing extenuating factors when rendering a sentence.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.P('Effect on Incarceration Rate', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P("At the heart of the argument is whether TIS is having any effect on crime or incarceration rates. As shown below, the statistics seem to indicate that states with more strigent TIS policies tend to see higher rates of both crime and incarceration. If these policies inherently led to higher rates of incarceration, it would be natural to expect a corresponding trend in new court commitments. Since this isn't the case, one might reasonably conclude that TIS policies have, at best, no effect on the incarceration rate and, at worst, a negative impact.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=3)
						], style={'border': 'none'}),						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(['TIS Policy:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_tis', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Sentencing', 'TIS policy'), 
									value='tisp', 
									placeholder='Select a variable', 
									id='dd_indep_tis', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_tis', style={'width': '800px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),

						############################
						# Sentencing structure
						############################
						html.Tr([
							html.Td([
								html.P('Sentencing Structure', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P("Like TIS policies, codified sentence structures don't necessarily correspond to lower incarceration and/or crime rates. A number of sentencing structures were examined, including presumptive sentencing (those which are codified into law) and determinate sentencing (sentencing with a defined length of time). It can be seen below that states with determinate sentencing have comparable incarceration rates but higher crime rates.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=3)
						], style={'border': 'none'}),						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(['Sentencing structure:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_ss', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Sentencing', 'Sentencing structure'), 
									value='pre_guid', 
									placeholder='Select a variable', 
									id='dd_indep_ss', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_ss', style={'width': '800px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),

					############################
					# Demographics
					############################
					html.Table([
						html.Tr([
							html.Td([
								html.P('Other Factors', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
								html.P("Obviously this is a complex issue with a number of factors at play, ranging from socio-economic factors to spending on law enforcement. We'll examine some of these influencing factors.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Img(src=imgPath + 'img_demo.jpg', height='200px'),
								html.P('Demographics', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P("Crime and incarceration rates are often linked to demographic factors such as population rates, the relative number of people living in major metropolitan areas, and the proportion of young people living in the state. As such, these factors should be considered as control variables in any forecasting model that is built. As shown below, crime and incarceration rates are, notably, heavily influenced by various demographic factors. Perhaps unexpectedly, there is a strong correlation between crime rate and the number of people aged 25 to 34, while states having high percentages of people aged 18-24 exhibit and inverse relationship to most outcome variables.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=3)
						], style={'border': 'none'}),						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(['Demographics:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_demo', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Control', 'Demographics'), 
									value='pop_l1', 
									placeholder='Select a variable', 
									id='dd_indep_demo', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'})
						], style={'border': 'none', 'padding': '0px'}),  # tr
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_demo', style={'width': '800px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),

						############################
						# Economy
						############################
						html.Tr([
							html.Td([
								html.Img(src=imgPath + 'img_econ.jpg', height='200px'),
								html.P('Economy', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P("Along with demographic factors, economic indicators also influence incarceration rates. This is especially apparent when comparing outcome variables against the Gini coefficient--a value that signifies how much a state's income distribution deviates from an equal distribution. Lower values of Gini coefficient indicate a more equal distribution. Surprisingly, crime rates also trended positively with per capita income, although it is likely that states with higher incomes also have higher Gini rates.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=3)
						], style={'border': 'none'}),						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(['Economy:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_econ', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Control', 'Economy'), 
									value='incpc_l1', 
									placeholder='Select a variable', 
									id='dd_indep_econ', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_econ', style={'width': '800px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),

						############################
						# Society
						############################
						html.Tr([
							html.Td([
								html.Img(src=imgPath + 'img_soc.jpg', height='200px'),
								html.P('Society', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P("Conventional wisdom would seem to indicate that states having more conservative populations--and, therefore, more conservative government and societal ideologies--would also experience higher incarceration rates and lower crime rates. However, some key indicators would suggest otherwise. Notably, there didn't seem to be any significant difference in incarceration rates in states having Republican governors or those in which a high proportion of the population adhere to a fundamentalist religion.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=3)
						], style={'border': 'none'}),						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(['Society:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_soc', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Control', 'Society'), 
									value='religion', 
									placeholder='Select a variable', 
									id='dd_indep_soc', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_soc', style={'width': '800px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),

						############################
						# Corrections
						############################
						html.Tr([
							html.Td([
								html.Img(src=imgPath + 'img_corr.jpg', height='200px'),
								html.P('Corrections', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P("It isn't surprising that any statistic that measures crime or incarceration rate would correlate to higher expenditures on corrections and law enforcement. Of course, one couldn't conclude that law enforcement was the *cause* of criminal activity. Those with a favourable outlook of the criminal justice system might be inclined to conclude that that the more money spent, the more crime is detected and mitigated, while those critical of the law enforcement might have the opposite take--that the police are overly vigilant and exercise a greater authority than warranted. In either case, the statistics show an obvious correlation between law enforcement spending and rates of crime and incarceration.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=3)
						], style={'border': 'none'}),						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(['Corrections:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_corr', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Control', 'Corrections'), 
									value='expcorr_', 
									placeholder='Select a variable', 
									id='dd_indep_corr', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_corr', style={'width': '800px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=3)
						], style={'border': 'none', 'padding': '0px'})

					############################
					# Close tables
					############################
					], style={'border-collapse': 'collapse', 'padding': '0px', 'border': 'none'})
				], style={'border': 'none', 'padding': '0px'}, colSpan=2)
			], style={'border': 'none', 'padding': '0px'}),
		], style={'border-collapse': 'collapse', 'padding': '0px', 'border': 'none'}),
		html.Div(id='dummy_div')  # dummy div to signal app to load data
	], style={'margin': 'auto', 'width': '50%', 'padding': '10px'}
)

#-----------------------------------------------------

# Callback functions to update map
@app.callback(
	Output('gr_map1', 'figure'),
	Output('gr_map2', 'figure'),
	Output('gr_map3', 'figure'),
	Output('lbl_map_title', 'children'),
	Input('dummy_div', 'id'),
	Input('sl_year', 'value'),
	prevent_initial_call=False
)
def update_map1(dummy_div, sl_year):

	# Fetch data
	dfplot = df1[df1['year'] == sl_year]
	#dfplot['tmp_agg'] = np.where((dfplot['pre_par']=='yes') | (dfplot['presum_s']=='yes'), 'yes', 'no')

	# Display map1 - tiss
	fig1 = px.choropleth(dfplot, locations='state_ab', locationmode='USA-states', scope='usa', color='tiss', color_discrete_map={'no': 'cornsilk', 'yes': 'cadetblue'}, width=500)
	fig1.update_layout(
		plot_bgcolor='white',
		title={'text': 'Truth-in-Sentencing Policy - ' + str(sl_year), 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9}
	)

	# Display map2 - aggregated presumptive guidelines
	fig2 = px.choropleth(dfplot, locations='state_ab', locationmode='USA-states', scope='usa', color='tisviol_agg', color_discrete_map={'no': 'cornsilk', 'yes': 'cadetblue'}, width=500)
	fig2.update_layout(
		plot_bgcolor='white',
		title={'text': 'Minimum sentence required for violent crime - ' + str(sl_year), 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9}
	)

	# Display map3 - mean tisp
	#dfplot_mean = dfplot[dfplot['tiss'] == 'yes'].groupby(['year'], as_index=False).agg({'tisp': 'mean'})
	##dfplot_mean = dfplot.groupby(['year'], as_index=False).apply(lambda x: np.average(x.tisp, weights=x.pop_l1))
	#dfplot_mean.columns.values[1] = 'tisp'
	#fig3 = px.bar(dfplot_mean, orientation='h', x='tisp', y='pre_par', height=120, width=600)
	#fig3.update_layout(
	#	plot_bgcolor='white',
	#	title={'text': 'Mean percentage of sentence offenders required to serve - ' + str(sl_year), 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9},
	#	yaxis={'visible': False, 'showticklabels': False},
	#	xaxis={'title': '', 'range': [0, 100]}
	#)

	# Display map3 - mean tisp by presence of determinate sentencing
	dfplot_mean = dfplot.groupby(['pre_par'], as_index=False).agg({'tisp': 'mean'})
	dfplot_mean.columns.values[1] = 'tisp'
	fig3 = px.bar(dfplot_mean, orientation='h', x='tisp', y='pre_par', height=180, width=600)
	fig3.update_layout(
		plot_bgcolor='white',
		title={'text': 'Mean % of sentence required (by determinate sentencing) - ' + str(sl_year) , 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9},
		yaxis={'title': '', 'visible': True, 'showticklabels': True},
		xaxis={'title': '', 'range': [0, 100]}
	)

	# Return
	return fig1, fig2, fig3, 'Truth-in-Sentencing Policies - ' + str(sl_year)

"""
# Callback functions for play/stop button
@app.callback(
	Output('ani_map', 'disabled'),
	Output('but_play', 'value'),
	Input('but_play', 'n_clicks'),
	Input('ani_map', 'disabled'),
	prevent_initial_call=True
)
def enable_animate(but_play, ani_map):

	# Update interval object
	print('here1', ani_map, but_play)
	if but_play % 1 == 1:
		print('here2', ani_map, but_play)
		return False, 'Stop'
	else:
		print('here5', ani_map, but_play)
		return True, 'Play'
	print('here6', ani_map, but_play)
	return False, 'Stop'

# Callback functions to animate map
@app.callback(
	Output('sl_year', 'value'),
	Input('sl_year', 'value'),
	Input('ani_map', 'disabled'),
	prevent_initial_call=False
)
def animate_map1(sl_year, ani_map):

	# Update slider year
	print('here3', ani_map)
	newyr = sl_year
	if not ani_map:
		print('here4', ani_map)
		newyr += 3
		if newyr > 2002: newyr = 1975

	# Return
	return newyr
"""

#-----------------------------------------------------

# Callback functions to update tis graph
@app.callback(
	Output('gr_tis', 'figure'),
	Input('dd_outcome_tis', 'value'),
	Input('dd_indep_tis', 'value'),
	prevent_initial_call=False
)
def update_gr_tis(outcome_var, indep_var):
	try:
		r = update_gr_general(outcome_var, indep_var)
		return r
	except:
		return {}

# Callback functions to update demographics graph
@app.callback(
	Output('gr_demo', 'figure'),
	Input('dd_outcome_demo', 'value'),
	Input('dd_indep_demo', 'value'),
	prevent_initial_call=False
)
def update_gr_demo(outcome_var, indep_var):
	try:
		r = update_gr_general(outcome_var, indep_var)
		return r
	except:
		return {}

# Callback functions to update economy graph
@app.callback(
	Output('gr_econ', 'figure'),
	Input('dd_outcome_econ', 'value'),
	Input('dd_indep_econ', 'value'),
	prevent_initial_call=False
)
def update_gr_econ(outcome_var, indep_var):
	try:
		r = update_gr_general(outcome_var, indep_var)
		return r
	except:
		return {}

# Callback functions to update society graph
@app.callback(
	Output('gr_soc', 'figure'),
	Input('dd_outcome_soc', 'value'),
	Input('dd_indep_soc', 'value'),
	prevent_initial_call=False
)
def update_gr_soc(outcome_var, indep_var):
	try:
		r = update_gr_general(outcome_var, indep_var)
		return r
	except:
		return {}

# Callback functions to update economy graph
@app.callback(
	Output('gr_corr', 'figure'),
	Input('dd_outcome_corr', 'value'),
	Input('dd_indep_corr', 'value'),
	prevent_initial_call=False
)
def update_gr_corr(outcome_var, indep_var):
	try:
		r = update_gr_general(outcome_var, indep_var)
		return r
	except:
		return {}

# Callback functions to update sentence structure graph
@app.callback(
	Output('gr_ss', 'figure'),
	Input('dd_outcome_ss', 'value'),
	Input('dd_indep_ss', 'value'),
	prevent_initial_call=False
)
def update_gr_ss(outcome_var, indep_var):
	try:
		r = update_gr_general(outcome_var, indep_var)
		return r
	except:
		return {}

#-----------------------------------------------------

# Run dash app
if __name__ == "__main__":
	app.run_server(debug=True, processes=1, threaded=True)

