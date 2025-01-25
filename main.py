from bayut_scanner import BayutScraper
import pandas as pd
import streamlit as st
from utils import validate_location, cache_key


def show_dashboard():
    # Page config
    scraper = BayutScraper()
    st.set_page_config(
        page_title="Bayut Property Finder", page_icon="🏠", layout="wide"
    )
    st.title("🏠 Bayut Property Finder (UAE)")
    st.markdown("##### Bills included propeties only (water and electricity)")
    search_button = None

    # Sidebar filters
    with st.sidebar:
        st.header("Search Filters")

        # Update location input with clearer instructions
        st.markdown("### Location")
        st.markdown("Examples: khalifa city, al reem island, al raha beach")

        # List of suggestions
        suggestions = ["Khalifa City", "Masdar City", "Al Rayyana"]

        area_suggestions = ["Abu Dhabi", "Dubai"]
        area = st.selectbox("Area:", area_suggestions)
        # selected_location = st.selectbox("Select a location:", suggestions)
        selected_location = st.text_input(label="Location")

        # Automatically format the full location string
        location = (
            f"{area.lower()}, {selected_location.lower()}"
            if selected_location
            else ""
        )

        price_range = st.slider(
            "Price Range (AED)",
            min_value=0,
            max_value=100000,
            value=(0, 50000),
            step=10000,
        )

        rooms = st.selectbox(
            "Number of Bedrooms",
            options=[str(i) for i in range(1, 7)] + ["7+"],
            index=0,
        )
        baths = st.selectbox(
            "Number of Bathrooms",
            options=[str(i) for i in range(1, 3)],
            index=0,
        )
        page_count = st.selectbox(
            "Maximum Pages to check",
            options=[i for i in range(1, 4)],
            index=0,
        )

        search_button = st.button("Search Properties")
    # Main content
    if search_button:
        if not selected_location:
            st.error("Please enter an area name")
            return
        if not validate_location(location):
            st.error("Please enter a valid area name (e.g., khalifa city)")
            return

        # # Create cache key based on search parameters
        # key = cache_key(location, price_range, rooms)

        # # Check cache first
        # @st.cache_data(ttl=3600)
        def fetch_properties(location, min_price, max_price, rooms, baths):
            return scraper.search_properties(
                location=location,
                min_price=min_price,
                max_price=max_price,
                rooms=rooms,
                baths=baths,
                max_page_count=page_count,
            )

        with st.spinner("Searching properties..."):
            results = fetch_properties(
                location, price_range[0], price_range[1], rooms, baths
            )

            if not results:
                st.warning("No properties found matching your criteria")
                return

            # Display results
            st.subheader(f"Found {len(results)} properties")

            # Convert to DataFrame for better display
            df = pd.DataFrame(results)

            # Display properties in a grid
            cols = st.columns(2)
            for idx, row in df.iterrows():
                with cols[idx % 2]:
                    with st.container():
                        st.image(row["image_url"], use_container_width=True)
                        st.markdown(f"**{row['title']}**")
                        st.write(f"💰 Price: AED {row['price']}")
                        # st.write(f"🛏️ {row['bedrooms']}")
                        st.write(f"📍 {row['location']}")
                        # if row['amenities']:
                        #     st.write("✨ " + ", ".join(row['amenities'][:3]))
                        st.markdown(f"[View Property]({row['url']})")
                        st.divider()


def main():
    show_dashboard()
    # export_data(results)
    # print(results)


def export_data(results):
    # convert dictionary to dataframe
    df = pd.DataFrame(results)
    excel_file = "properties.xlsx"
    csv_file = "properties.csv"
    df.to_csv(csv_file)
    df.to_excel(excel_file, index=False)
    print("File Exported!!")


if __name__ == "__main__":
    main()
