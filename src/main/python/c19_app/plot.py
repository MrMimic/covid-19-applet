#!/usr/bin/env python3

from c19 import plot_clusters
from sklearn.decomposition import PCA
from plotly import graph_objs as go
import json
import plotly


def combine_doi_and_sentences(sub_df):
    """ Add link to paper DOI to scatter points """
    sentences = sub_df["sentence_split"]
    dois = sub_df["paper_doi"]
    data = [
        f'{s}<br /><a href="https://www.doi.org/{d}" target="_blank">{d}</a>'
        for d, s in zip(dois, sentences)
    ]
    return data


def scatter(params, df):
    """ Method to plot the DF """

    # Reduce vectors dimensions
    pca = PCA(n_components=2)
    # vectors = [json.loads(x) for x in df.vector.to_list()]
    vector_reduced = pca.fit_transform(df.vector.to_list())
    df["x"] = [vector[0] for vector in vector_reduced]
    df["y"] = [vector[1] for vector in vector_reduced]

    # Split raw sentences and join them back with <BR /> for prettier output
    df["sentence_split"] = [
        plot_clusters.add_br_every(s, 7) for s in df.raw_sentence.to_list()
    ]

    data = []
    # Here we should get multi scatter foreach cluster with "name" attribute
    # Color as well should be set foreach
    for cluster_id in df["cluster"].unique():
        sub_df = df[df["cluster"] == cluster_id]
        sub_plot = go.Scatter(x=sub_df["x"],
                              y=sub_df["y"],
                              mode="markers",
                              hovertext=combine_doi_and_sentences(sub_df),
                              name=f"Cluster {cluster_id}",
                              customdata=['https://www.baidu.com'] *
                              sub_df.shape[0],
                              hoverinfo="text")
        data.append(sub_plot)

    # THat stuff should go to a config file
    layout = go.Layout(yaxis={
        "visible": True,
        "showgrid": True,
        "zeroline": False,
        "showticklabels": False
    },
                       xaxis={
                           "visible": True,
                           "showgrid": True,
                           "zeroline": False,
                           "showticklabels": False
                       },
                       margin={
                           "l": 50,
                           "r": 50,
                           "b": 50,
                           "t": 20,
                           "pad": 0
                       },
                       showlegend=True,
                       legend={"orientation": "h"},
                       hovermode="closest")

    figure = dict(data=data, layout=layout)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
