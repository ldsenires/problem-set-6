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
    ui.input_switch("switch", "Toggle to switch to range of hours", value=False),
    ui.panel_conditional(
        "input.switch",
        ui.input_slider("range_slider", "Select hour of the day:",
                    min=0, max=23, value=[6, 9], step=1),
        ui.output_plot("layered_plot_range")
    ),
    ui.panel_conditional(
        "!input.switch",
        ui.input_slider("hour_slider", "Select hour of the day:",
                    min=0, max=23, value=0, step=1),
        ui.output_plot("layered_plot_single")
    )
)


def server(input, output, session):
    @reactive.calc
    def load_top_alerts():
        return pd.read_csv("top_alerts_map_byhour.csv")

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
    def input_range():
        filtered_data = input_alert()

        if input.switch:
            range_hour = []

            for index in range(0,2):
                if input.range_slider()[index] < 10:
                    selected_hour = "0" + str(input.range_slider()[index]) + ":00"
                else:
                    selected_hour = str(input.range_slider()[index]) + ":00"
            
                range_hour.append(selected_hour)

            if range_hour:
                filtered_data_range = filtered_data[
                    (filtered_data["hour"] >= range_hour[0]) & (
                        filtered_data["hour"] <= range_hour[1])
                ]
                return filtered_data_range
    
    @reactive.calc
    def input_hour():
        filtered_data = input_alert()

        if input.hour_slider() < 10:
            selected_hour = "0" + str(input.hour_slider()) + ":00"
        else:
            selected_hour = str(input.hour_slider()) + ":00"
            
        if selected_hour:
            filtered_data_byhour = filtered_data[
                (filtered_data["hour"] == selected_hour)
                ]
            return filtered_data_byhour

    @reactive.calc
    def load_geojson():
        return gpd.read_file("chicago-boundaries.geojson")
    
    @render.plot
    def layered_plot_range():
        base_data = load_geojson()
        fig, ax = plt.subplots()
        base_data.plot(ax=ax, color="lightgray", edgecolor="white")
        
        scatter_data = input_range()
        ax.scatter(scatter_data["longitude"], scatter_data["latitude"])
        
        minx, miny, maxx, maxy = base_data.total_bounds
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

        return fig

    @render.plot
    def layered_plot_single():
        base_data = load_geojson()
        fig, ax = plt.subplots()
        base_data.plot(ax=ax, color="lightgray", edgecolor="white")
        
        scatter_data = input_hour()
        ax.scatter(scatter_data["longitude"], scatter_data["latitude"])
        
        minx, miny, maxx, maxy = base_data.total_bounds
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

        return fig


app = App(app_ui, server)
