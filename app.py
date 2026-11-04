import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Netflix Titles EDA Dashboard",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #141414;
    color: white;
}
h1, h2, h3 {
    color: #E50914;
}
[data-testid="stMetric"] {
    background-color: #252525;
    padding: 18px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Netflix Titles EDA Dashboard")
st.write("Explore Netflix movies and TV shows using data analysis and visualization.")

uploaded_file = st.file_uploader(
    "Upload Netflix Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Remove duplicate records
    df = df.drop_duplicates()

    # Clean text columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Convert year to numeric
    if "release_year" in df.columns:
        df["release_year"] = pd.to_numeric(
            df["release_year"], errors="coerce"
        )

    # Fill missing values for analysis
    for col in ["type", "rating", "country", "listed_in", "director"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    st.success("Dataset loaded and cleaned successfully!")

    # Sidebar filters
    st.sidebar.header("Dashboard Filters")

    filtered_df = df.copy()

    if "type" in df.columns:
        types = sorted(df["type"].dropna().unique().tolist())
        selected_types = st.sidebar.multiselect(
            "Select Content Type",
            types,
            default=types
        )

        filtered_df = filtered_df[
            filtered_df["type"].isin(selected_types)
        ]

    if "release_year" in filtered_df.columns:
        years = filtered_df["release_year"].dropna()

        if not years.empty:
            min_year = int(years.min())
            max_year = int(years.max())

            selected_years = st.sidebar.slider(
                "Select Release Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )

            filtered_df = filtered_df[
                filtered_df["release_year"].between(
                    selected_years[0], selected_years[1]
                )
            ]

    if "rating" in filtered_df.columns:
        ratings = sorted(
            filtered_df["rating"].dropna().unique().tolist()
        )

        selected_ratings = st.sidebar.multiselect(
            "Select Rating",
            ratings,
            default=ratings
        )

        filtered_df = filtered_df[
            filtered_df["rating"].isin(selected_ratings)
        ]

    # KPI metrics
    total_titles = len(filtered_df)

    if "type" in filtered_df.columns:
        movies = (filtered_df["type"] == "Movie").sum()
        shows = (filtered_df["type"] == "TV Show").sum()
    else:
        movies = 0
        shows = 0

    if "country" in filtered_df.columns:
        countries = (
            filtered_df["country"]
            .replace("Unknown", pd.NA)
            .dropna()
            .str.split(", ")
            .explode()
            .nunique()
        )
    else:
        countries = 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Titles", f"{total_titles:,}")
    c2.metric("Movies", f"{movies:,}")
    c3.metric("TV Shows", f"{shows:,}")
    c4.metric("Countries", f"{countries:,}")

    st.divider()

    # Charts row 1
    left, right = st.columns(2)

    with left:
        st.subheader("Movies vs TV Shows")

        if "type" in filtered_df.columns:
            type_counts = (
                filtered_df["type"]
                .value_counts()
                .reset_index()
            )
            type_counts.columns = ["type", "count"]

            fig = px.pie(
                type_counts,
                names="type",
                values="count",
                hole=0.45,
                title="Content Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Titles by Release Year")

        if "release_year" in filtered_df.columns:
            yearly = (
                filtered_df.dropna(subset=["release_year"])
                .groupby("release_year")
                .size()
                .reset_index(name="count")
            )

            fig = px.line(
                yearly,
                x="release_year",
                y="count",
                markers=True,
                title="Netflix Titles Released Each Year"
            )

            st.plotly_chart(fig, use_container_width=True)

    # Charts row 2
    left, right = st.columns(2)

    with left:
        st.subheader("Top 10 Countries")

        if "country" in filtered_df.columns:
            country_data = (
                filtered_df["country"]
                .replace("Unknown", pd.NA)
                .dropna()
                .str.split(", ")
                .explode()
            )

            top_countries = (
                country_data.value_counts()
                .head(10)
                .reset_index()
            )

            top_countries.columns = ["country", "count"]

            fig = px.bar(
                top_countries,
                x="count",
                y="country",
                orientation="h",
                title="Countries with the Most Titles"
            )

            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Content Ratings")

        if "rating" in filtered_df.columns:
            rating_data = (
                filtered_df["rating"]
                .value_counts()
                .reset_index()
            )

            rating_data.columns = ["rating", "count"]

            fig = px.bar(
                rating_data,
                x="rating",
                y="count",
                title="Titles by Rating"
            )

            st.plotly_chart(fig, use_container_width=True)

    # Genre analysis
    if "listed_in" in filtered_df.columns:
        st.subheader("Top 10 Genres")

        genres = (
            filtered_df["listed_in"]
            .dropna()
            .str.split(", ")
            .explode()
        )

        top_genres = (
            genres.value_counts()
            .head(10)
            .reset_index()
        )

        top_genres.columns = ["genre", "count"]

        fig = px.bar(
            top_genres,
            x="count",
            y="genre",
            orientation="h",
            title="Most Common Genres"
        )

        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    # Dataset table
    st.divider()
    st.subheader("📋 Filtered Netflix Dataset")

    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Dataset",
        data=csv_data,
        file_name="filtered_netflix_titles.csv",
        mime="text/csv"
    )

    # Basic insights
    st.divider()
    st.subheader("📊 Dataset Insights")

    st.write(f"- The filtered dataset contains **{total_titles:,} titles**.")

    if movies + shows > 0:
        if movies > shows:
            st.write("- Movies are more common than TV Shows in the filtered dataset.")
        elif shows > movies:
            st.write("- TV Shows are more common than Movies in the filtered dataset.")
        else:
            st.write("- Movies and TV Shows have equal counts in the filtered dataset.")

    if "release_year" in filtered_df.columns:
        valid_years = filtered_df["release_year"].dropna()

        if not valid_years.empty:
            st.write(
                f"- Release years range from **{int(valid_years.min())}** "
                f"to **{int(valid_years.max())}**."
            )

else:
    st.info("Please upload your Netflix CSV dataset to view the dashboard.")

    st.markdown("""
    ### Dashboard Features
    - Total titles, movies, and TV shows
    - Interactive filters
    - Movies vs TV Shows chart
    - Titles by release year
    - Top countries
    - Content ratings
    - Popular genres
    - Filtered dataset and CSV download
    """)