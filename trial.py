import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Real Estate Dashboard & Target Distribution", layout="wide")
st.title("🏙️ Dubai Real Estate Dashboard & Target Distribution")

# --- File Upload ---
uploaded_file = "new_tdf.csv"

# --- IQR Bound Helper ---
def get_iqr_bounds(df, col):
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in DataFrame for IQR calculation.")
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

# --- Target Distribution Function ---
def plot_target_distribution_by_object_columns_streamlit(dfs, target, df_names):
    object_cols = [
        'trans_group_en', 'procedure_name_en', 'property_type_en', 'property_sub_type_en',
        'property_usage_en', 'reg_type_en', 'nearest_landmark_en', 'nearest_metro_en',
        'nearest_mall_en', 'rooms_en'
    ]

    for i, df in enumerate(dfs):
        df_name = df_names[i]
        st.header(f"📊 Target Distribution Analysis for: {df_name}")

        if target not in df.columns:
            st.warning(f"Target column '{target}' not found in {df_name}. Skipping this dataset.")
            continue

        fig = px.box(df, y=target, title=f'Overall Boxplot of {target} ({df_name})')
        fig.update_layout(yaxis_title="Meter Sale Price (AED)", yaxis_tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    for col in object_cols:
        st.subheader(f"📌 Box & Line Plots by: {col}")
        cols = st.columns(len(dfs))

        for i, df in enumerate(dfs):
            df_name = df_names[i]
            if col not in df.columns:
                continue

            with cols[i]:
                st.markdown(f"**{df_name}**")

                fig_box = px.box(df, x=col, y=target, title=f'Box Plot by {col} ({df_name})')
                fig_box.update_layout(yaxis_title="Meter Sale Price (AED)", yaxis_tickformat=",")
                st.plotly_chart(fig_box, use_container_width=True)

                # Use normalized column names consistently here
                year_col = None
                for c in ['instance_year', 'instance_Year', 'instance_year']:  # normalized
                    if c in df.columns:
                        year_col = c
                        break

                if year_col is not None:
                    grouped_data = df.groupby([year_col, col])[target].mean().reset_index()
                    fig_line = px.line(
                        grouped_data, x=year_col, y=target, color=col,
                        title=f'Line Plot by {year_col} and {col} ({df_name})'
                    )
                    fig_line.update_layout(
                        xaxis_title="Year", yaxis_title="Meter Sale Price (AED)",
                        yaxis_tickformat=",", legend_title=col
                    )
                    fig_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("---")

# --- Main Logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
