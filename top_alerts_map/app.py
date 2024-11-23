from shiny import App, render, ui, reactive
import pandas as pd
import altair as alt
import json
import matplotlib.pyplot as plt
import geopandas as gpd

app_ui = ui.page_fluid(
    ui.panel_title("Top 10 Highest Count Per Alert Type and Subtype"),
    ui.input_select(
        id = "alerts",
        label = "Choose 'Type - Subtype' Combination:",
        choices = []
    ),
    ui.output_plot("layered_plot")
)


def server(input, output, session):
    @reactive.calc
    def load_top_alerts():
        return pd.read_csv("top_alerts_map.csv")

    @reactive.effect
    def _():
        alert_type = load_top_alerts()["updated_type"]
        alert_subtype = load_top_alerts()["updated_subtype"]
        alert_combined = alert_type + " - " + alert_subtype
        alert_list = alert_combined.unique().tolist()
        alert_list = sorted(alert_list)
        ui.update_select("alerts", choices=alert_list)

    @reactive.calc
    def input_alert():
        alert_data = load_top_alerts()
        selected_alert = input.alerts()
        if selected_alert:
            selected_type, selected_subtype = selected_alert.split(" - ")
            filtered_data = alert_data[
                (alert_data["updated_type"] == selected_type) &
                (alert_data["updated_subtype"] == selected_subtype)
            ]
            return filtered_data

    @reactive.calc
    def load_geojson():
        return gpd.read_file("chicago-boundaries.geojson")
    
    @render.plot
    def layered_plot():
        base_data = load_geojson()
        fig, ax = plt.subplots()
        base_data.plot(ax=ax, color="lightgray", edgecolor="white")
        
        scatter_data = input_alert()
        ax.scatter(scatter_data["longitude"], scatter_data["latitude"])
        
        minx, miny, maxx, maxy = base_data.total_bounds
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

        return fig


app = App(app_ui, server)
