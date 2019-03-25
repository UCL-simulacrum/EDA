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
