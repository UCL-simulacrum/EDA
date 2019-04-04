"""
SimuLacrum Analysis Package (SLAP)
This module contains functions used by the UCL simulacrum team to analyse the
simulacrum cancer data set.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.offline as po
import plotly.graph_objs as go
from plotly import tools
import load
import descriptions
import random

# Layout variables for plots
font = dict(family='Courier New, monospace',
            size=14,
            color='#000000')
useable_groupings = ['DEATHCAUSECODE_UNDERLYING_DESC', 'ETHNICITY_DESC',
                     'DEATHLOCATIONCODE_DESC', ]
# AV Patient frequency plot


av_fr_titles = {'DEATHCAUSECODE_UNDERLYING_DESC': "Underlying Death Cause",
                'ETHNICITY_DESC': 'Ethnicity Provided',
                'DEATHLOCATIONCODE_DESC': "Location"}


def frequency_plot_layout(search_var):
    x_axis = go.layout.XAxis(automargin=True,
                             title=av_fr_titles[search_var],
                             titlefont=font)

    y_axis = dict(title="Counts",
                  titlefont=font
                  )

    plt_title = "Frequency of Death by " + av_fr_titles[search_var]

    return go.Layout(title=plt_title,
                     xaxis=x_axis,
                     yaxis=y_axis)


def stacked_barplot(df, col1, col2, tickmode='auto'):
    """
    Creates a stacked bar plot with col1 as the stacked bars
    and col2 on the x-axis

    df: dataframe containing col1 and col2 as columns
    col1: name of column as string
    col2: name of column as string
    tickmode: when == 'linear', show all x-axis labels
    """

    # Get dataframe of col1,col2 and frequency of people with that col1/col2
    df = df[[col1, col2]] \
        .groupby([col2, col1]) \
        .agg({col1: 'size'}) \
        .rename(columns={col1: 'count'}) \
        .reset_index()

    # pivot the table in the correct format for a stacked bar plot
    df = df.pivot(index=col2, columns=col1)['count']
    x = df.index

    # create plotly plot
    data = []

    np.random.seed(seed=7)

    for stack in df.keys():
        color = np.random.randint(255, size=(1, 3))[0]

        trace = go.Bar(
            x=[str(i) for i in x],
            y=df[stack],
            name=stack, marker=dict(color='rgb({}, {}, {})'.format(*color)))

        data.append(trace)

    layout = go.Layout(barmode='stack', hovermode='closest',
                       xaxis=dict(title=col2.capitalize(), 
                                  tickmode=tickmode,
                                  titlefont = font),
                       yaxis=dict(title="Count",
                                  titlefont = font))

    fig = go.Figure(data=data, layout=layout)

    po.iplot(fig)


def av_patient_frequency(av_patient, search_var, topN = 20):
    top = av_patient[search_var].value_counts()[1:topN].keys()
    top = av_patient.loc[av_patient[search_var].isin(top)]

    topbysex = top.groupby(['SEX', search_var]) \
        .agg({search_var: 'size'})

    male = topbysex.loc['1'][search_var]
    female = topbysex.loc['2'][search_var]

    # plotly plots
    trace1 = go.Bar(
        x=female.index,
        y=female.values,
        name='female'
    )
    trace2 = go.Bar(
        x=male.index,
        y=male.values,
        name='male'
    )

    data = [trace1, trace2]

    if search_var in useable_groupings:

        layout = frequency_plot_layout(search_var)

    else:
        layout = go.Layout(
            barmode='group'
        )

    fig = go.Figure(data=data, layout=layout)
    po.iplot(fig)
    
def Sequenceofevents(df_full_patient_pathways,event_types,dates):
    """Creates a dataframe with the sequence of event per patient, 
    where each row would be one event. The event_types are chosen
    from the columns of df_full_patient_pathways, and there dates
    are columns from df_full_patient_pathways also"""
    
    df_pathway_events = pd.DataFrame()
    
    for date, event_type in zip(dates,event_types):

        #get the events and event dates,
        #we must drop duplicates as some are replicated due to the merging
        #in cancerdata_EDA
        df = df_full_patient_pathways[['PATIENTID', date, event_type]].drop_duplicates()
        df = df.rename(index=str, columns={date:'date', event_type:'event'})

        #any event with 'N either means 
        #NO(nothing happend) or not known(for outcome summary)'
        df = df[df['event'] != 'N']

        df['event_type'] = event_type

        #get rid of NaN events
        df = df[df['event'].notnull()]

        #some drug group values are the same as there regimen values
        df['event'] = df['event_type'] + " " + df['event'].astype(str)

        #stack the events and event dates
        df_pathway_events = pd.concat([df_pathway_events,df])

    df_pathway_events = df_pathway_events.sort_values(by = ['PATIENTID','date'])
    
    #Now convert dates to number of days passed since first event. 
    #The Simulacrum imitates data in 2013-2017 : https://simulacrum.healthdatainsight.org.uk/available-data/
    #so we should remove dates below these
    
    #remove years below 2013
    correct_years = pd.to_datetime(df_pathway_events['date']).apply(lambda date: date.year)>2012
    df_pathway_events = df_pathway_events[correct_years]

    #make a column 'days' which has the number of days
    #since the first event of a given patient
    df_dates = df_pathway_events[['PATIENTID','date']]
    df_dates['date'] = pd.to_datetime(df_dates['date'])

    #dates of the first event of a patient
    df_start_dates = df_dates.groupby('PATIENTID').first().reset_index().rename(columns={'date':'start date'})

    #days from the first event of a patient
    df_dates = pd.merge(df_dates,df_start_dates,how='left')
    df_dates['days'] = df_dates['date']-df_dates['start date']
    df_pathway_events['days'] = [d.days for d in df_dates['days']]

    #remove nans
    df_pathway_events = df_pathway_events[df_pathway_events['days'].notnull()]
    
    #add diagnosis of patient as a column
    df_cancers = df_full_patient_pathways[['PATIENTID','PRIMARY_DIAGNOSIS']].drop_duplicates()
    df_pathway_events = pd.merge(df_pathway_events,df_cancers,how='left',on='PATIENTID')
    
    return df_pathway_events

def plotevents(df_event_vector,event_types):
    """plotly plot of events colour coded by event_types
    df_event_vector: a dataframe with columns 'event_label','x','y','event_type','event' """
    data=[]
    color = np.random.seed(seed=20)
    for event_type in event_types:
        color=np.random.randint(255, size=(1, 3))[0]
        x = df_event_vector[df_event_vector['event_type']==event_type]['x']
        y = df_event_vector[df_event_vector['event_type']==event_type]['y']
        events = df_event_vector[df_event_vector['event_type']==event_type]['event']
        trace = go.Scatter( x = x,
                            y = y,
                            mode = 'markers',
                            text = events,
                            hoverinfo = 'text',
                            name = event_type,
                            marker = dict(size = 3,
                                          color = 'rgb({}, {}, {})'.format(*color)) )
        data.append(trace)

    layout = dict(title = 'Visualisation of events',
                  yaxis = dict(zeroline = False,
                               title = "word2vec feature 2"),
                  xaxis = dict(zeroline = False,
                               title = "word2vec feature 1")
                 )

    fig = dict(data=data, layout=layout)
    po.iplot(fig)
    
def plotpathways(df_sequences,topN,map2D):
    """plots pathways by adding up the vectors of each event in a sequence
    df_sequences:dataframe with a 'sequence' column that has lists of events in a sequence
    topN: plots the topN cancers
    map2D: maps the event label to it's vector"""
    data=[]
    
    top5cancers = df_sequences['PRIMARY_DIAGNOSIS'].value_counts().keys()[:topN]

    np.random.seed(seed=20)
    for c in top5cancers:

        color = np.random.randint(255, size=(1, 3))[0]

        c_sequences = df_sequences[df_sequences['PRIMARY_DIAGNOSIS'] == c]
        c_sequences100 = random.choices(list(c_sequences['sequence']),k=100)

        legend = True
        for s in c_sequences100:
            event_vectors = np.array([list(map2D[e]) for e in s])
            pathway_coordinates = np.cumsum(event_vectors, axis=0)


            trace = go.Scatter( x = pathway_coordinates[:,0],
                                y = pathway_coordinates[:,1],
                                mode = 'lines',
                                name = c,
                                legendgroup = c,
                                line=dict(width=1,
                                          color='rgb({}, {}, {})'.format(*color)), 
                                showlegend = legend)
            legend = False
            data.append(trace)

    layout = dict(title = 'Visualisation of pathways',
                  yaxis = dict(zeroline = False,
                               title = "word2vec feature 2"),
                  xaxis = dict(zeroline = False,
                               title = "word2vec feature 1")
                 )

    fig = dict(data=data, layout=layout)
    po.iplot(fig)

def plotendpoints_alivedead(df_sequences, topN, map2D):
    """plots endpoints of pathways. First colours by alive/dead then by cancer type.
    df_sequences:dataframe with a 'sequence' column that has lists of events in a sequence
    topN: plots the topN cancers
    map2D: maps the event label to it's vector
    """
    
    count_alive_dead = df_sequences['NEWVITALSTATUS_DESC'].value_counts()[:2]
    total_alive_dead = count_alive_dead.sum()

    fig = tools.make_subplots(rows=2, cols=2, subplot_titles=('Coloured by Alive/Dead, Cartesian',
                                                              'Coloured by Alive/Dead, Polar',
                                                              'Coloured by cancer type, Cartesian',
                                                              'Coloured by cancer type, Polar'))

    np.random.seed(seed=20)
    for c in count_alive_dead.keys():

        color = np.random.randint(255, size=(1, 3))[0]

        c_sequences = df_sequences[df_sequences['NEWVITALSTATUS_DESC'] == c]
        c_sequences100 = random.choices(list(c_sequences['sequence']),k=2000*count_alive_dead[c]//total_alive_dead)

        legend = True
        end_coordinates_x = []
        end_coordinates_y = []
        end_coordinates_r = []
        end_coordinates_t = []
        for s in c_sequences100:
            event_vectors = np.array([list(map2D[e]) for e in s])
            end_coordinates = np.sum(event_vectors, axis=0)
            end_coordinates_x.append(end_coordinates[0])
            end_coordinates_y.append(end_coordinates[1])
            end_coordinates_r.append(np.sqrt(end_coordinates[0]**2 + end_coordinates[1]**2))
            end_coordinates_t.append(np.arctan2(end_coordinates[1], end_coordinates[0]))

        trace_cartesian = go.Scatter( x = end_coordinates_x,
                            y = end_coordinates_y,
                            mode = 'markers',
                            name = c,
                            opacity = 1,
                            marker=dict(size=1,color='rgb({}, {}, {})'.format(*color)), 
                            showlegend = legend)

        trace_polar = go.Scatter( x = end_coordinates_t,
                            y = end_coordinates_r,
                            mode = 'markers',
                            name = c,
                            opacity = 1,
                            marker=dict(size=1,color='rgb({}, {}, {})'.format(*color)), 
                            showlegend = legend)
        legend = False

        fig.append_trace(trace_cartesian, 1, 1)
        fig.append_trace(trace_polar, 1, 2)

    count_top_cancers = df_sequences['PRIMARY_DIAGNOSIS'].value_counts()[:topN]
    total_top_cancers = count_alive_dead.sum()

    np.random.seed(seed=20)
    for c in count_top_cancers.keys():

        color = np.random.randint(255, size=(1, 3))[0]

        c_sequences = df_sequences[df_sequences['PRIMARY_DIAGNOSIS'] == c]
        c_sequences100 = random.choices(list(c_sequences['sequence']),k=2000*count_top_cancers[c]//total_top_cancers)

        legend = True
        end_coordinates_x = []
        end_coordinates_y = []
        end_coordinates_r = []
        end_coordinates_t = []
        for s in c_sequences100:
            event_vectors = np.array([list(map2D[e]) for e in s])
            end_coordinates = np.sum(event_vectors, axis=0)
            end_coordinates_x.append(end_coordinates[0])
            end_coordinates_y.append(end_coordinates[1])
            end_coordinates_r.append(np.sqrt(end_coordinates[0]**2 + end_coordinates[1]**2))
            end_coordinates_t.append(np.arctan2(end_coordinates[1], end_coordinates[0]))

        trace_cartesian = go.Scatter( x = end_coordinates_x,
                            y = end_coordinates_y,
                            mode = 'markers',
                            name = c,
                            opacity = 1,
                            marker=dict(size=1,color='rgb({}, {}, {})'.format(*color)), 
                            showlegend = legend)

        trace_polar = go.Scatter(x = end_coordinates_t,
                                 y = end_coordinates_r,
                                 mode = 'markers',
                                 name = c,
                                 opacity = 1,
                                 marker=dict(size=1,color='rgb({}, {}, {})'.format(*color)), 
                                 showlegend = legend)
        legend = False

        fig.append_trace(trace_cartesian, 2, 1)
        fig.append_trace(trace_polar, 2, 2)

    fig['layout'].update(title='Visualising ends of patient pathways')

    po.iplot(fig)

def sequenceclusterplot(df_single_cancer,feature_space):
    """plot the TFIDF representation of a sequence
    
    df_single_cancer: has columns 'cluster', 'x','y'
    where 'cluster' is the cluster the patient belongs to
    and 'x,y' are it's feature co-ordinates"""

    data=[]
    color = np.random.seed(seed=21)

    clusters = df_single_cancer['cluster'].unique()
    for c in sorted(clusters):
        color=np.random.randint(255, size=(1, 3))[0]
        x = df_single_cancer[df_single_cancer['cluster']==c]['x']
        y = df_single_cancer[df_single_cancer['cluster']==c]['y']
        text = 'cluster: ' + c.astype(str) + '<br>'
        text = text + 'PATIENTID: ' + df_single_cancer[df_single_cancer['cluster']==c]['PATIENTID'].astype(str)
        text = text + '<br> sequence: ' + df_single_cancer[df_single_cancer['cluster']==c]['sequence'].astype(str)
        trace = go.Scattergl( x = x,
                            y = y,
                            mode = 'markers',
                            name = str(c),
                            text = text,
                            hoverinfo  = 'text',
                            legendgroup = str(c),
                            marker = dict(size = 4,
                                          color = 'rgb({}, {}, {})'.format(*color)) )
        data.append(trace)

    layout = dict(title = 'Each point here represents a sequence in the {} features space'.format(feature_space),
                  yaxis = dict(zeroline = False,
                               title = "{} sequence feature 2".format(feature_space)),
                  xaxis = dict(zeroline = False,
                               title = "{} sequence feature 1".format(feature_space))
                 )

    fig = dict(data=data, layout=layout)
    po.iplot(fig)

def clusterinfo(df_single_cancer,
                df_pathway_events,
                single_cancer,
                top=5,
                display=['REGIMEN_OUTCOME_SUMMARY',
                         'BENCHMARK_GROUP',
                         'DRUG_GROUP']):

    #get df_pathway_events of the single cancer
    df_single_cancer_seq = df_pathway_events[df_pathway_events['PRIMARY_DIAGNOSIS']==single_cancer]

    #add the cluster labels into the df_single_cancer_seq
    df_single_cancer_seq = pd.merge(df_single_cancer_seq,df_single_cancer[['PATIENTID','cluster']], how = 'left')

    #cluster freq
    cluster_freq = df_single_cancer[['PATIENTID', 'cluster']]['cluster'].value_counts()
    df_cluster_freq = pd.DataFrame({'cluster': cluster_freq.keys(),'cluster_freq':cluster_freq.values})    

    #remove the event type in the 'event' column
    df_single_cancer_seq['event'] = [e[len(et)+1:] for e,et in
                                    zip(df_single_cancer_seq['event'],df_single_cancer_seq['event_type'])]
    df_single_cancer_seq = df_single_cancer_seq[df_single_cancer_seq['event_type'].isin(display)]

    #make the top event_types as columns and use the events frequencies as rows

    dfc = df_single_cancer_seq.groupby(['cluster','event_type','event']).agg({'event':'count'}).rename(columns={'event':'event_%'})
    dfc = dfc.groupby(['cluster','event_type']).apply(lambda x: round(100*x/x.sum(),1))
    

    dfc = dfc.reset_index().groupby(['cluster','event_type']).apply(lambda x: x.nlargest(top,'event_%'))
    dfc = dfc.reset_index(drop=True)
    dfc['event'] = dfc['event_%'].astype(str) + "% " + dfc['event']
    dfc

    dfc['top'] = dfc.groupby(['cluster','event_type']).cumcount()+1
    dfc['event_type'] = dfc['event_type'] + " " + dfc['top'].astype(str)
    dfc = dfc.pivot(values='event',columns='event_type',index='cluster').reset_index()



    #get mean days in sequence with standard deviation
    df_single_cancer['total days in sequence'] = df_single_cancer['sequence_days'].apply(lambda x: x[-1])
    dfcmean = df_single_cancer.groupby('cluster')[['total days in sequence']].apply(lambda x: round(x.mean()).astype(int) ).reset_index().rename(columns = {'total days in sequence':'mean'})
    dfcstd = u"\u00B1" + " " + df_single_cancer.groupby('cluster')[['total days in sequence']].apply(lambda x: round(x.std()).astype(int) ).reset_index().rename(columns = {'total days in sequence':'std'})['std'].astype(str) 
    dfcmean['days in sequence'] = dfcmean['mean'].astype(str) + " " + dfcstd
    
    #merge all information
    df = pd.merge(dfcmean[['cluster','days in sequence']], dfc)
    df = pd.merge(df_cluster_freq,df,on='cluster')
    df = df.sort_values(by=['cluster'])
    df = df.reset_index(drop=True)
    
    return df
    
 
