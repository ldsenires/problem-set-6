from shiny import App, render, ui, reactive
import pandas as pd
import altair as alt
import json
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.panel_title("Top 10"),
    ui.input_select(
        id = "alerts",
        label = "pick:",
        choices = []
    ),
    ui.output_plot("scatter_plot")
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

    @render.plot
    def scatter_plot():
        scatter_data = input_alert()
        fig, ax = plt.subplots()
        ax.scatter(scatter_data["latitude"], scatter_data["longitude"])
        return fig




app = App(app_ui, server)
