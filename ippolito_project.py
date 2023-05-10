# Load libraries
from dash import Dash, dcc, html, Input, Output
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re
import sys
import time

#-----------------------------------------------------

# Init vars
offline = False
if offline:
	url_vars = 'data/vars.tsv'
	url_abbr = 'data/state_abbr.csv'
	url_data1 = 'data/04456-0001-Data.tsv'
	url_pred = 'data/predicted.csv'
	url_cat = 'data/cat.csv'
	imgPath = 'https://github.com/mmippolito/cuny_data608_final_project/raw/main/'
else:
	url_vars = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/vars.tsv'
	url_abbr = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/state_abbr.csv'
	url_data1 = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/04456-0001-Data.tsv'
	url_pred = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/predicted.csv'
	url_cat = 'https://raw.githubusercontent.com/mmippolito/cuny_data608_final_project/main/data/cat.csv'
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

# Define function to populate category dropdown list
def populate_cat_dd():

	# Populate dategory dropdown list
	d = {dfcat.iloc[x]['title']: dfcat.iloc[x]['title'] for x in range(0, dfcat.shape[0])}
	return d

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
def update_gr_general(outcome_var, indep_var, chk):

	# Copy chk_options
	#chk_options2 = chk_options.copy()

	# Check for error
	if outcome_var is None or indep_var is None:
		print('returning empty dict')
		return {}, {}, chk_options

	# Find missing value [value]
	miss_outcome = dfvar[dfvar['var'] == outcome_var]['missing'].values[0]
	miss_indep = dfvar[dfvar['var'] == indep_var]['missing'].values[0]

	# Fetch data
	dfplot1 = df1[(df1[outcome_var] != miss_outcome) & (df1[indep_var] != miss_indep) & (df1[indep_var] != 'na')]

	# Plot
	if dfvar[dfvar['var'] == indep_var]['vartype'].values[0] == 'cat':
		#chk_options2[0]['label'] = 'Flip categories'
		if len(chk) > 0:
			fig1 = px.box(dfplot1, x=indep_var, y=outcome_var, color='year', width=500, height=400, points='outliers', \
				color_discrete_sequence=['burlywood', 'darkgoldenrod', 'chocolate', 'cornflowerblue', 'cadetblue', 'darkgreen', 'darkorchid', 'darkmagenta', 'crimson', 'deeppink'])
		else:
			fig1 = px.box(dfplot1, x='year', y=outcome_var, color=indep_var, width=500, height=400, points='outliers', \
				color_discrete_sequence=['burlywood', 'cadetblue'])
	else:
		#chk_options2[0]['label'] = 'Show trendline'
		if len(chk) > 0:
			fig1 = px.scatter(dfplot1, x=indep_var, y=outcome_var, color='year', width=500, height=400, color_continuous_scale='deep_r', trendline="ols")
		else:
			fig1 = px.scatter(dfplot1, x=indep_var, y=outcome_var, color='year', width=500, height=400, color_continuous_scale='deep_r')
	fig1.update_xaxes(mirror=False, showline=True, ticks='outside', linecolor='black', gridcolor='lightgrey', title=dfvar[dfvar['var'] == indep_var]['descr'].values[0])
	fig1.update_yaxes(mirror=False, showline=True, ticks='outside', linecolor='black', gridcolor='lightgrey', title=dfvar[dfvar['var'] == outcome_var]['descr'].values[0])
	fig1.update_layout(title='', plot_bgcolor='white')

	# Display map
	dfplot1 = dfplot1[dfplot1['year'] == 2002]
	if dfvar[dfvar['var'] == indep_var]['vartype'].values[0] == 'cat':
		fig2 = px.choropleth(dfplot1, locations='state_ab', locationmode='USA-states', scope='usa', color=indep_var, color_discrete_sequence=['cadetblue', 'cornsilk'], width=500)
	else:
		fig2 = px.choropleth(dfplot1, locations='state_ab', locationmode='USA-states', scope='usa', color=indep_var, color_continuous_scale='deep', width=500)
	fig2.update_layout(
		plot_bgcolor='white',
		title={'text': dfvar[dfvar['var'] == indep_var]['descr'].values[0] + ' - 2002', 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9, 'font': {'family': 'Calibri', 'size': 14}}
	)

	# Return plot
	return fig1, fig2, chk_options

#-----------------------------------------------------

# Load data
dfvar = load_data(url_vars, '\t')
dfabbr = load_data(url_abbr, ',')
df1 = load_data(url_data1, '\t')
dfpred = load_data(url_pred, ',')
dfcat = load_data(url_cat, ',')

# Set checklist options
chk_options = [{'label': 'Set option', 'value': 1, 'disabled': False}]

# Merge state abbreviations
df1 = pd.merge(df1, dfabbr, on='state_na', how='inner')
dfpred = pd.merge(dfpred, dfabbr, on='state_na', how='inner')
# Create dict for year slider
d_yr = {str(x): str(x) for x in df1['year'].unique()}

# Copy HOL variables to second subcategory
df1['hol_2str2'] = df1['hol_2str']
df1['hol_3str2'] = df1['hol_3str']

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
df1['hol_2str2'] = np.where(df1['hol_2str2']==0, 'no', np.where(df1['hol_2str2']==1, 'yes', 'na'))
df1['hol_3str2'] = np.where(df1['hol_3str2']==0, 'no', np.where(df1['hol_3str2']==1, 'yes', 'na'))
df1['hol_drug'] = np.where(df1['hol_drug']==0, 'no', np.where(df1['hol_drug']==1, 'yes', 'na'))
df1['hol_vio'] = np.where(df1['hol_vio']==0, 'no', np.where(df1['hol_vio']==1, 'yes', 'na'))
df1['hol_sex'] = np.where(df1['hol_sex']==0, 'no', np.where(df1['hol_sex']==1, 'yes', 'na'))

# Set aggregated policy data - c('tiss', 'tisviol', 'pre_guid', 'pre_volg', 'pre_par', 'rec_sent', 'presum_s', 'pre_rec_')
df1.loc[:, 'policy_agg'] = np.where((df1['pre_guid']=='yes') | (df1['pre_volg']=='yes') | (df1['pre_par']=='yes') | \
	(df1['rec_sent']=='yes') | (df1['presum_s']=='yes') | (df1['pre_rec_']=='yes'), 'yes', 'no')

# Set aggregated mandatory sentencing for violent offenders - m10_we1a==1 | m16_we2a==1 | m22_we3a==1 | m28_we4a==1 | m52_vi1a==1 | m58_vi2a==1
df1.loc[:, 'tisviol_agg'] = np.where((df1['m10_we1a']==1) | (df1['m16_we2a']==1) | (df1['m22_we3a']==1) | \
	(df1['m28_we4a']==1) | (df1['m52_vi1a']==1) | (df1['m58_vi2a']==1), 'yes', 'no')

# Mean incarceration rates
df_inc = df1.groupby(['year'], as_index=False).agg({'inc_rate': 'mean'})

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
					html.Img(src=imgPath + 'img_prison.jpg', height='360px'),
					html.Br(),
					html.Br(),
					html.P('An Uneven System', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
					html.P("Before the 1990s, many prisoners incarcerated in the US criminal justice system only served a fraction of their sentence, often being released for good behavior or other mitigating factors. These factors were applied unevenly at the discretion of parole boards. Public pressure led to the passage of the Violent Crime Control and Law Enforcement Act (VCCLEA) in 1994, which gave incentives to states that required prisoners to serve at least 85% of their sentence. These so-called truth-in-sentencing (TIS) laws are still heavily debated.", 
						style={'font-size': '14px', 'text-align': 'left'}
					),
					html.P("We'll examine various aspects of TIS, first by looking at when TIS laws were adopted state by state. Then we'll see what factors affect various outcome variables such as incarceration and crime rates. Lastly, we'll evaluate whether TIS is having its desired effect.", 
						style={'font-size': '14px', 'text-align': 'left'}
					),
				], style={'border': 'none', 'padding': '0px', 'text-align': 'center'}, colSpan=2),
			], style={'border': 'none'}),

			############################
			# State map - TISS
			############################
			html.Tr([
				html.Td([
					html.Label(id='lbl_map_title', children=['Truth-in-Sentencing Policies Over the Years'])
				], style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=2),
			], style={'border': 'none', 'padding': '0px'}),
			html.Tr([
				html.Td([
					dcc.Graph(id='gr_map1', style={'width': '600px'})
				], style={'border': 'none', 'padding': '0px'}, colSpan=1),
				html.Td([
					dcc.Graph(id='gr_map2', style={'width': '600px'})
				], style={'border': 'none', 'padding': '0px'}, colSpan=1)
			], style={'border': 'none', 'padding': '1px'}),
			html.Tr([
				html.Td([
					dcc.Graph(id='gr_map3', style={'width': '600px'})
				], style={'font-size': '14px', 'border': 'none', 'padding': '1px'}, colSpan=1),
			], style={'border': 'none', 'padding': '0px'}),
			html.Tr([
				html.Td([
					dcc.Slider(id='sl_year', min=1975, max=2002, step=3, value=1975, marks=d_yr, updatemode='drag')
					#html.Button(id='but_play', value='Play', n_clicks=0, disabled=False),
					#dcc.Interval(id="ani_map", disabled=True)
				], style={'border': 'none', 'padding': '1px', 'text-align': 'left'}, colSpan=1)
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
					html.Table([

						############################
						# Pros & Cons
						############################
						html.Tr([
							html.Td([
								html.Img(src=imgPath + 'img_tis.jpg', height='200px'),
								html.P('Pros and "Cons"', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
								html.P("Arguments leading to passage of the VCCEA included that truth in sentencing (TIS) laws would deter future criminal behavior, would render justice to the perpetrator for the crime commited, and that time served would theoretically be unbiased and no longer at the whim of a parole board. Opponents of TIS argue that TIS leads to prison overcrowding, that the cost of incarcerating prisoners longer could be better spent on crime prevention programs, that it disincentivizes good behavior, and that it in fact does not serve as a deterrent to future crime. Further, it leaves judges no room in weighing extenuating factors when rendering a sentence. And in a criminal justice system that many accuse of being implicitly biased, the net result could simply mean more underrepresented people are spending more time behind bars.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=4)
						], style={'border': 'none'}),

						############################
						# Factors
						############################
						html.Tr([
							html.Td([
								html.P('What factors affect incarceration rate?', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
								html.P("Obviously this is a complex issue with a number of factors at play, ranging from socio-economic factors to spending on law enforcement. We'll examine some of these influencing factors, starting with the one with the most direct influence: truth-in-sentencing policies.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Td([
									dcc.Dropdown(
										options=populate_cat_dd(), 
										value='TIS Policies', 
										placeholder='Select a category', 
										id='dd_cat', 
										style={'width': '400px', 'font-size': '12px'}
									)
								], style={'border': 'none', 'padding': '0px'}),
								html.Br(),
								html.Img(id='img_dyn', src='', height='200px'),
								html.P(id='p_title_dyn', children='', style={'font-size': '16px', 'font-weight': 'bold', 'text-decoration': 'underline', 'text-align': 'left'}),
								html.P(id='p_text_dyn', children='', style={'font-size': '14px', 'text-align': 'left'}),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=4)
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label(id='lbl_dyn', children='')
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'border': 'none', 'padding': '1px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_dyn', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								dcc.Checklist(
									options=chk_options,
									value=[],
									id='chk_dyn',
									style={'font-size': '14px'}
								)
							], style={'width': '90px', 'border': 'none', 'padding': '1px'}),
							html.Td([
								dcc.Dropdown(
									options={}, 
									value='', 
									placeholder='Select a variable', 
									id='dd_indep_dyn', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'width': '40px', 'border': 'none', 'padding': '1px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_dyn', style={'width': '500px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=2),
							html.Td([
								dcc.Graph(id='map_dyn', style={'width': '500px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=2)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=4)
						], style={'border': 'none', 'padding': '0px'}),

						############################
						# Is TIS working?
						############################
						html.Tr([
							html.Td([
								html.Img(src=imgPath + 'img_tis_effect.jpg', height='200px'),
								html.P('Is TIS working?', style={'font-size': '21px', 'font-weight': 'bold', 'text-align': 'left'}),
								html.P("The question of whether TIS is having the desired effect is complex and varies greatly depending on ideology. For some, TIS is an attempt at detering crime while applying justice fairly and equally. For others, the goal may be less about deterrence and more about rendering sentencing. For those in the latter camp, incarceration and/or crime rates may not even be considered factors of success, with the only goal being to increase sentence lengths.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.P("Regardless of ideology, we can examine trends in outcomes like crime and incarceration rates to evaluate what effect it may be having. To do this, a linear model was created based on pre-1994 statistics (i.e., before the VCCLEA was passed). Outcome statistics were predicted for post 1994 and compared to actual statistics reported during those years. The results are below.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
								html.Br()
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=4)
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								html.Label(['Outcome:'])
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'border': 'none', 'padding': '1px'}),
							html.Td([
								html.Label('')
							], style={'font-weight': 'bold', 'font-size': '12px', 'border': 'none', 'padding': '0px'}),
							html.Td([
								html.Label([''])
							], style={'border': 'none', 'padding': '1px'})
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								dcc.Dropdown(
									options=populate_dd('Outcome', '.'), 
									value='inc_rate', 
									placeholder='Select an outcome variable', 
									id='dd_outcome_tiseff', 
									style={'width': '400px', 'font-size': '12px'}
								)
							], style={'border': 'none', 'padding': '0px'}),
							html.Td([
								dcc.Checklist(
									options={'1': 'Show mean annual values'},
									value=[],
									id='chk_mean',
									style={'font-size': '14px'}
								)
							], style={'border': 'none', 'padding': '0px'}, colSpan=2),
							html.Td([
								html.Label([''])
							], style={'border': 'none', 'padding': '1px'})
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								dcc.Graph(id='gr_tiseff', style={'width': '500px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=2),
							html.Td([
								dcc.Graph(id='map_tiseff', style={'width': '500px'})
							], style={'border': 'none', 'padding': '0px'}, colSpan=2)
						], style={'border': 'none', 'padding': '0px'}),  #tr
						html.Tr([
							html.Td([
								html.P("As seen above, the predicted incarceration rate without TIS laws is significantly lower than the actual rate. This seems to counter the prediction that prison admissions would have been higher absent TIS laws, but it is likely that this is simply a reflection of the growing overall population. Overall crime rates seem unaffected by TIS, while violent crime rate was predicted to have been higher without TIS. Since TIS mostly applies to violent offenses, this would seem to indicate it is at least partially working.", 
									style={'font-size': '14px', 'text-align': 'left'}
								),
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=4)
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=4)
						], style={'border': 'none', 'padding': '0px'}),
						html.Tr([
							html.Td([
								html.P('References', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'left'}),
								html.P(children=["Stemen, D. ", html.I("Impact of State Sentencing Policies on Incarceration Rates in the United States, 1975-2002 (ICPSR 4456)."), " (2007, September 27). Inter-university Consortium for Political and Social Research. https://www.icpsr.umich.edu/web/NACJD/studies/4456."], style={'font-size': '12px', 'text-align': 'left'}),
								html.P(children=["Ditton, P. Wilson, D. & BJS Statisticians. ", html.I("Truth in Sentencing in State Prisons."), " (1999, January). Bureau of Justice. https://bjs.ojp.gov/content/pub/pdf/tssp.pdf."], style={'font-size': '12px', 'text-align': 'left'}),
								html.P(children=["Shorey, J. ", html.I("Truth in Sentencing Overview & Laws."), " (2022, May 4). Study.com. https://study.com/learn/lesson/truth-in-sentencing-overview-laws.html."], style={'font-size': '12px', 'text-align': 'left'}),
								html.P(children=[html.I("State Good Time and Earned Time Laws (2021, June 11)."), " National Conference of State Legislatures. https://www.ncsl.org/civil-and-criminal-justice/state-good-time-and-earned-time-laws."], style={'font-size': '12px', 'text-align': 'left'}),
								html.P(children=[html.I("Know More: Truth-in-Sentencing."), " (2020). Restore Justice Foundation. https://www.restorejustice.org/about-us/resources/know-more/know-more-truth-in-sentencing/."], style={'font-size': '12px', 'text-align': 'left'}),
								html.P(children=[html.I("Federal Sentencing Guidelines: Background, Legal Analysis, and Policy Options."), " (2009, March 16). EveryCRSReport. https://www.everycrsreport.com/reports/RL32766.html."], style={'font-size': '12px', 'text-align': 'left'}),
								html.P(children=[html.I("Metadata Glossary."), " (2023). World Bank, https://databank.worldbank.org/metadataglossary/gender-statistics/series/SI.POV.GINI."], style={'font-size': '12px', 'text-align': 'left'})
							], style={'text-align': 'left', 'border': 'none', 'padding': '1px', 'height': '40px', 'text-align': 'center'}, colSpan=4)
						], style={'border': 'none'}),
						html.Tr([
							html.Td([
								html.Hr()
							], style={'font-size': '14px', 'border': 'none', 'padding': '1px', 'height': '40px'}, colSpan=4)
						], style={'border': 'none', 'padding': '0px'})

					############################
					# Close tables
					############################
					], style={'border-collapse': 'collapse', 'padding': '0px', 'border': 'none'})
				], style={'border': 'none', 'padding': '0px'}, colSpan=2)
			], style={'border': 'none', 'padding': '0px'}),
		], style={'border-collapse': 'collapse', 'padding': '0px', 'border': 'none'}),
		html.Div(id='dummy_div')  # dummy div to signal app to load data
	], style={'margin': 'auto', 'width': '60%', 'padding': '10px'}
)

#-----------------------------------------------------

# Callback functions to update map
@app.callback(
	Output('gr_map1', 'figure'),
	Output('gr_map2', 'figure'),
	Output('gr_map3', 'figure'),
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
		title={'text': 'Truth-in-Sentencing Policy - ' + str(sl_year), 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9, 'font': {'family': 'Calibri', 'size': 18}}
	)

	# Display map2 - aggregated presumptive guidelines
	fig2 = px.choropleth(dfplot, locations='state_ab', locationmode='USA-states', scope='usa', color='tisviol_agg', color_discrete_map={'no': 'cornsilk', 'yes': 'cadetblue'}, width=500)
	fig2.update_layout(
		plot_bgcolor='white',
		title={'text': 'Mandatory sentencing for violent crime - ' + str(sl_year), 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9, 'font': {'family': 'Calibri', 'size': 18}}
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
		title={'text': 'Mean % of sentence required (by determinate sentencing) - ' + str(sl_year) , 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9, 'font': {'family': 'Calibri', 'size': 18}},
		yaxis={'title': '', 'visible': True, 'showticklabels': True},
		xaxis={'title': '', 'range': [0, 100]}
	)

	# Return
	return fig1, fig2, fig3

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

# Callback functions to update dynamic options
@app.callback(
	Output('img_dyn', 'src'),
	Output('dd_indep_dyn', 'options'),
	Output('p_title_dyn', 'children'),
	Output('p_text_dyn', 'children'),
	Output('lbl_dyn', 'children'),
	Input('dd_cat', 'value'),
	prevent_initial_call=False
)
def update_dyn_options(dd_cat):
	try:
		ser = dfcat[dfcat['title'] == dd_cat]
		src = imgPath + ser['img'].values[0] + '.jpg'
		d = populate_dd(ser['cat'].values[0], ser['subcat'].values[0])
		ttl = ser['title'].values[0]
		txt = ser['text'].values[0]
		lbl = ser['label'].values[0]
		return src, d, ttl, txt, lbl
	except:
		return '', {}, '', '', ''

# Callback functions to update dynamic graphs
@app.callback(
	Output('gr_dyn', 'figure'),
	Output('map_dyn', 'figure'),
	Output('chk_dyn', 'options'),
	Input('dd_outcome_dyn', 'value'),
	Input('dd_indep_dyn', 'value'),
	Input('chk_dyn', 'value'),
	prevent_initial_call=False
)
def update_dyn_gr(outcome_var, indep_var, chk):
	try:
		r1, r2, chk = update_gr_general(outcome_var, indep_var, chk)
		return r1, r2, chk
	except:
		return {}, {}, {}

# Callback functions to update tis effect graphs
@app.callback(
	Output('gr_tiseff', 'figure'),
	Output('map_tiseff', 'figure'),
	Input('dd_outcome_tiseff', 'value'),
	Input('chk_mean', 'value'),
	prevent_initial_call=False
)
def update_gr_tiseff(outcome_var, chk_mean):

	if outcome_var is None:
		print('returning empty dict')
		return {}

	# Fetch data
	dfplot1 = dfpred

	# Plot
	if len(chk_mean) > 0:

		# Mean
		dfplot2 = dfplot1.groupby(['year', 'val_type'], as_index=False).agg({outcome_var: 'mean'})
		fig1 = px.line(dfplot2, x='year', y=outcome_var, color='val_type', width=600, height=400, markers=True)

	else:

		# All values
		fig1 = px.strip(dfplot1, x='year', y=outcome_var, color='val_type', width=600, height=400, stripmode='group')

	# Axes
	fig1.update_xaxes(mirror=False, showline=True, ticks='outside', linecolor='black', gridcolor='lightgrey', title='year')
	fig1.update_yaxes(mirror=False, showline=True, ticks='outside', linecolor='black', gridcolor='lightgrey', title=dfvar[dfvar['var'] == outcome_var]['descr'].values[0])
	fig1.update_layout(title='', plot_bgcolor='white')

	# Choose year for map; some vars are NaN for 2002
	mapyr = 2002
	if outcome_var == 'adm_100k' or outcome_var == 'ncourtc' or outcome_var == 'court_10':
		mapyr = 1996
	dfplot1 = dfplot1[dfplot1['year'] == mapyr]

	# Map
	if dfvar[dfvar['var'] == outcome_var]['vartype'].values[0] == 'cat':
		fig2 = px.choropleth(dfplot1, locations='state_ab', locationmode='USA-states', scope='usa', color=outcome_var, color_discrete_sequence=['cadetblue', 'cornsilk'], width=500)
	else:
		fig2 = px.choropleth(dfplot1, locations='state_ab', locationmode='USA-states', scope='usa', color=outcome_var, color_continuous_scale='deep', width=500)
	fig2.update_layout(
		plot_bgcolor='white',
		title={'text': dfvar[dfvar['var'] == outcome_var]['descr'].values[0] + ' - ' + str(mapyr), 'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': 0.9, 'font': {'family': 'Calibri', 'size': 18}}
	)

	# Return plot
	return fig1, fig2

#-----------------------------------------------------

# Run dash app
if __name__ == "__main__":
	app.run_server(debug=True, processes=1, threaded=True)

#-----------------------------------------------------
