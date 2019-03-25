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
    x_axis = dict(title=av_fr_titles[search_var],
                  titlefont=font
                  )
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
                       xaxis=dict(title=col2, tickmode=tickmode),
                       yaxis=dict(title="COUNT"))

    fig = go.Figure(data=data, layout=layout)

    po.iplot(fig)


def av_patient_frequency(av_patient, search_var):
    top20 = av_patient[search_var].value_counts()[1:20].keys()
    top20 = av_patient.loc[av_patient[search_var].isin(top20)]

    top20bysex = top20.groupby(['SEX', search_var]) \
        .agg({search_var: 'size'})

    male = top20bysex.loc['1'][search_var]
    female = top20bysex.loc['2'][search_var]

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
