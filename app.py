"""
State Statutes Browser - Streamlit Dashboard with Supabase Integration
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Constants
TABLE_NAME = "state_statutes"
PAGE_SIZE = 100

# Page configuration
st.set_page_config(
    page_title="State Statutes Browser",
    page_icon="📜",
    layout="wide"
)


@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client using Streamlit secrets."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


@st.cache_data(ttl=600)
def fetch_states(_supabase: Client) -> list[str]:
    """Fetch list of available states."""
    response = _supabase.table(TABLE_NAME).select("state").eq("type", "law_text").execute()
    states = sorted(set(row["state"] for row in response.data))
    return states


@st.cache_data(ttl=600)
def get_total_count(_supabase: Client, state: str, search_term: str = "") -> int:
    """Get total count of law_text rows for a state."""
    query = (_supabase.table(TABLE_NAME)
             .select("id", count="exact")
             .eq("type", "law_text")
             .eq("state", state))

    if search_term:
        query = query.ilike("properties->>law_text", f"%{search_term}%")

    response = query.execute()
    return response.count or 0


@st.cache_data(ttl=600)
def fetch_law_texts(_supabase: Client, state: str, offset: int = 0, limit: int = PAGE_SIZE, search_term: str = "") -> pd.DataFrame:
    """Fetch paginated law_text rows for a state."""
    query = (_supabase.table(TABLE_NAME)
             .select("id, properties, state")
             .eq("type", "law_text")
             .eq("state", state))

    if search_term:
        query = query.ilike("properties->>law_text", f"%{search_term}%")

    response = query.range(offset, offset + limit - 1).execute()

    if not response.data:
        return pd.DataFrame()

    # Extract fields from properties
    rows = []
    for row in response.data:
        props = row.get("properties", {})
        rows.append({
            "id": row["id"],
            "state": row["state"],
            "title": props.get("title", ""),
            "citation": props.get("citation", ""),
            "url": props.get("url", ""),
            "law_text": props.get("law_text", "")
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=600)
def fetch_law_by_id(_supabase: Client, law_id: str) -> dict | None:
    """Fetch a single law by ID."""
    response = (_supabase.table(TABLE_NAME)
                .select("id, properties, state")
                .eq("id", law_id)
                .execute())

    if response.data:
        row = response.data[0]
        props = row.get("properties", {})
        return {
            "id": row["id"],
            "state": row["state"],
            "title": props.get("title", ""),
            "citation": props.get("citation", ""),
            "url": props.get("url", ""),
            "law_text": props.get("law_text", "")
        }
    return None


def show_detail_page(supabase: Client, law_id: str):
    """Display the detail page for a single law."""
    law = fetch_law_by_id(supabase, law_id)

    if not law:
        st.error("Law not found.")
        if st.button("Back to Browse"):
            st.query_params.clear()
            st.rerun()
        return

    # Back button
    if st.button("< Back to Browse"):
        st.query_params.clear()
        st.rerun()

    st.markdown("---")

    # Title
    st.title(law["title"] or "Untitled Section")

    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**State:** {law['state'].replace('_', ' ').title()}")
    with col2:
        if law["citation"]:
            st.markdown(f"**Citation:** {law['citation']}")
    with col3:
        if law["url"]:
            st.markdown(f"**URL:** {law['url']}")

    st.markdown("---")

    # Law text
    st.subheader("Full Text")
    law_text = law["law_text"]
    if law_text:
        # Display with proper formatting
        st.markdown(
            f"""<div style="padding: 20px; background-color: #f8f9fa;
                border-radius: 5px; line-height: 1.6;">
                {law_text.replace(chr(10), '<br>')}
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.info("No law text available.")


def show_browse_page(supabase: Client):
    """Display the main browse page."""
    st.title("State Statutes Browser")

    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = 0

    # Sidebar - State selection
    st.sidebar.header("Filters")

    with st.spinner("Loading states..."):
        states = fetch_states(supabase)

    if not states:
        st.warning("No states found in the database.")
        return

    # Format state names for display
    state_display = {s: s.replace("_", " ").title() for s in states}

    selected_state = st.sidebar.selectbox(
        "Select State",
        options=states,
        format_func=lambda x: state_display[x],
        on_change=lambda: setattr(st.session_state, 'page', 0)
    )

    # Search filter (server-side)
    search_term = st.sidebar.text_input(
        "Search in law texts",
        placeholder="Enter search term...",
        on_change=lambda: setattr(st.session_state, 'page', 0)
    )

    # Get total count
    total_count = get_total_count(supabase, selected_state, search_term)
    total_pages = max(1, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)

    if total_count == 0:
        st.warning(f"No law texts found for {state_display[selected_state]}.")
        return

    # Display metrics
    st.metric("Total Law Texts", f"{total_count:,}")
    st.markdown("---")

    # Pagination controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("First", disabled=st.session_state.page == 0):
            st.session_state.page = 0
            st.rerun()

    with col2:
        if st.button("Previous", disabled=st.session_state.page == 0):
            st.session_state.page -= 1
            st.rerun()

    with col3:
        st.markdown(f"<div style='text-align: center'>Page {st.session_state.page + 1} of {total_pages}</div>", unsafe_allow_html=True)

    with col4:
        if st.button("Next", disabled=st.session_state.page >= total_pages - 1):
            st.session_state.page += 1
            st.rerun()

    with col5:
        if st.button("Last", disabled=st.session_state.page >= total_pages - 1):
            st.session_state.page = total_pages - 1
            st.rerun()

    # Fetch current page of data
    offset = st.session_state.page * PAGE_SIZE
    with st.spinner("Loading law texts..."):
        df = fetch_law_texts(supabase, selected_state, offset, PAGE_SIZE, search_term)

    # Show range info
    start_row = offset + 1
    end_row = min(offset + PAGE_SIZE, total_count)
    st.caption(f"Showing rows {start_row:,} - {end_row:,} of {total_count:,}")

    # Add view link column
    df["view"] = df["id"].apply(lambda x: f"?id={x}")

    # Display table with link column
    st.dataframe(
        df[["state", "title", "view"]],
        use_container_width=True,
        column_config={
            "state": st.column_config.TextColumn("State", width="small"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "view": st.column_config.LinkColumn("View", display_text="View", width="small"),
        },
        hide_index=True
    )


def main():
    # Initialize Supabase connection
    try:
        supabase = init_supabase()
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        st.info("Please ensure your Supabase credentials are configured in `.streamlit/secrets.toml`")
        st.code("""
[supabase]
url = "https://your-project-id.supabase.co"
key = "your-anon-or-service-role-key"
        """)
        return

    # Check for detail page via query params
    law_id = st.query_params.get("id")

    if law_id:
        show_detail_page(supabase, law_id)
    else:
        show_browse_page(supabase)


if __name__ == "__main__":
    main()
