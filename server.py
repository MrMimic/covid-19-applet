#!/usr/bin/env python3


import numpy as np
import pandas as pd

from c19 import parameters as c19_parameters
from c19 import query_matching, text_preprocessing, clusterise_sentences, database_utilities, embedding
from flask import Flask, escape, render_template, request

from c19_app import security, reader, plot
from flask_caching import Cache
from flask.helpers import url_for
import os


LOCAL_DB_PATH = "/home/dynomante/projects/covid-19-kaggle/local_exec/articles_database_v14_02052020_test.sqlite"
LOCAL_EMBEDDING_PATH = "/home/dynomante/projects/covid-19-kaggle/w2v_parquet_file_new_version.parquet"
CACHE_TIME = 600
DEBUG = True

# TODO: Make these parameters as arguments
# TODO: Create an installation script
# TODO: Make these methods runable by a script

# Create app
app = Flask(__name__)

# Create cache
config = {
    "DEBUG": DEBUG,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": CACHE_TIME
}
app.config.from_mapping(config)
cache = Cache(app)

@cache.cached(timeout=CACHE_TIME, key_prefix="all_sentences")
def load_sentence_from_cache(params):
    """ That will create a cache with all sentences to be matched vs query """
    # Load pre-trained word vectors
    embedding_model = embedding.Embedding(
        parquet_embedding_path=params.embedding.local_path,
        embeddings_dimension=params.embedding.dimension,
        sentence_embedding_method=params.embedding.word_aggregation_method,
        weight_vectors=params.embedding.weight_with_tfidf)

    # Load sentences from SQLite
    all_db_sentences_original = query_matching.get_sentences_data(
        db_path=params.database.local_path)

    return all_db_sentences_original, embedding_model


def query_df(params, query):
    """ Use the lib to process the query """
    # Load cached sentences from SQLite
    all_db_sentences_original, embedding_model = load_sentence_from_cache(
        params)

    print(query)
    # TODO: increase threshold if too much sentences
    # TODO: The query should be also located in the df or propagated to be also plotted

    # Get K closest for each
    closest_sentences_df, query_logs = query_matching.get_k_closest_sentences(
        query=query,
        all_sentences=all_db_sentences_original,
        embedding_model=embedding_model,
        minimal_number_of_sentences=params.query.minimum_sentences_kept,
        similarity_threshold=params.query.cosine_similarity_threshold,
        return_logs=True)

    # Clusterise them
    closest_sentences_df, kmean_logs = clusterise_sentences.perform_kmean(
        k_closest_sentences_df=closest_sentences_df,
        number_of_clusters=params.query.number_of_clusters,
        k_min=params.query.k_min,
        k_max=params.query.k_max,
        min_feature_per_cluster=params.query.min_feature_per_cluster,
        return_logs=True)

    log_query = query_logs + kmean_logs
    return closest_sentences_df, log_query


def get_params():
    """ Return default param with updated value from input """
    # Get default parameters and adjust with user's input
    params = c19_parameters.Parameters(
        database=c19_parameters.Database(local_path=LOCAL_DB_PATH),
        embedding=c19_parameters.Embedding(local_path=LOCAL_EMBEDDING_PATH))

    try:
        params.query.cosine_similarity_threshold = float(
            request.form["sim_threshold"])
    except KeyError:
        pass
    try:
        params.query.minimum_sentences_kept = int(request.form["n_sentence"])
    except KeyError:
        pass
    try:
        int_number_cluster = int(request.form["number_cluster"])
        if int_number_cluster == 0:
            params.query.number_of_clusters = "auto"
        else:
            params.query.number_of_clusters = int_number_cluster
    except KeyError:
        pass

    try:
        params.query.min_feature_per_cluster = int(
            request.form["feature_per_cluster"])
    except KeyError:
        pass

    return params


def get_favicon_path():
    return url_for("static", filename="favicon.ico")


def create_output_report(query: str,
                         closest_sentences_df: pd.DataFrame,
                         db_path: str = LOCAL_DB_PATH,
                         task: str = None,
                         subtask: str = None,
                         top_x: int = 3) -> None:

    if closest_sentences_df is None:
        return []
    output = []
    number_of_kept_sentences = closest_sentences_df.shape[0]
    number_of_unique_papers = closest_sentences_df.paper_doi.unique().size
    number_of_clusters = closest_sentences_df.cluster.unique().size
    for cluster in sorted(closest_sentences_df.cluster.unique().tolist()):
        sub_df = closest_sentences_df[closest_sentences_df["cluster"] ==
                                      cluster].sort_values(by="distance",
                                                           ascending=False)
        for index, row in sub_df.head(top_x).iterrows():
            sub_output = {}
            # As a markdown list
            sub_output["sentence"] = row.raw_sentence
            sub_output["distance"] = row.distance
            sub_output["cluster"] = row.cluster
            sub_output["title"] = database_utilities.get_article(paper_doi=row.paper_doi, db_path=db_path)[0][4]
            sub_output["doi"] = row.paper_doi
            output.append(sub_output)
    return output


@app.route("/", methods=["GET", "POST"])
def main():
    """ Main route """

    # Query logs
    query_logs = []

    # Update params with user's settings
    params = get_params()

    # Get query
    default_user_query = "What do we know about Chloroquine to treat covid-19?"
    try:
        user_query = str(
            request.form["user_query"]
        ) if request.form["user_query"] != "" else default_user_query
    except KeyError:
        user_query = default_user_query

    # Validate user query
    validated_query, validation_log = security.validate_query(user_query)
    query_logs.append(validation_log)

    # Create plot as JSON data to be sent to Jinja
    json_plot = None
    if validated_query is not None:
        try:
            # Compute closest sentences DF
            closest_sentences_df, k_sentence_kmeans_logs = query_df(params, validated_query)
            query_logs += k_sentence_kmeans_logs
            # Create plot from that DF
            json_plot = plot.scatter(params, closest_sentences_df)
        except Exception as error:
            closest_sentences_df = None
            error_log = f"Issue with the query: {error}"
            query_logs.append(error_log)
    else:
        closest_sentences_df = None

    # Create a reader to get RST data
    rst_reader = reader.Reader(data_path=os.path.join("static", "texts"))

    # Create HTML context
    context = {
        "favicon_path": get_favicon_path(),
        # JSON plot and text output
        "plot": json_plot,
        "text_output": create_output_report(user_query, closest_sentences_df),
        # RST texts or logs to HTML
        "page_header": rst_reader.get_html_text(page="page_header"),
        "logs_header": rst_reader.get_html_text(page="logs"),
        "application_logs": query_logs,
        "about": rst_reader.get_html_text(page="about"),
        "how_does_it_work": rst_reader.get_html_text(page="tech_details"),
        "links": rst_reader.get_html_text(page="links"),
        # Selected options
        "query_last_value": user_query,
        "sim_threshold_last_value": params.query.cosine_similarity_threshold,
        "n_sentence_last_value": params.query.minimum_sentences_kept,
        "number_cluster_last_value": params.query.number_of_clusters,
        "feature_per_cluster_last_value": params.query.min_feature_per_cluster
    }
    # Return render template + context
    html_template = render_template("index.html", **context)
    return html_template


if __name__ == "__main__":
    # Run the server
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
