#!/usr/bin/env python3

from c19 import plot_clusters
from sklearn.decomposition import PCA
from plotly import graph_objs as go
import json
import os
import plotly
import anyconfig


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
    vector_reduced = pca.fit_transform(df.vector.to_list())
    df["x"] = [vector[0] for vector in vector_reduced]
    df["y"] = [vector[1] for vector in vector_reduced]

    # Split raw sentences and join them back with <BR /> for prettier output
    df["sentence_split"] = [
        plot_clusters.add_br_every(s, 7) for s in df.raw_sentence.to_list()
    ]

    # Creates a sub scatter for each cluster
    data = []
    for cluster_id in df["cluster"].unique():
        sub_df = df[df["cluster"] == cluster_id]
        sub_plot = go.Scatter(x=sub_df["x"],
                              y=sub_df["y"],
                              mode="markers",
                              hovertext=combine_doi_and_sentences(sub_df),
                              name=f"Cluster {cluster_id}",
                              hoverinfo="text")
        data.append(sub_plot)

    # Load layout for this graphe
    layout = go.Layout(
        **anyconfig.load(os.path.join("static", "config", "plot_layout.json")))

    # Export HTML as JSON to be loaded by JS
    figure = dict(data=data, layout=layout)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
