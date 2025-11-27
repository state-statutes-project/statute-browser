"""
State Statutes Browser - Streamlit Dashboard with Supabase Integration
"""

import html
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }

    /* Stat cards */
    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .stat-card .number {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
    }

    .stat-card .label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Result cards */
    .result-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .result-card:hover {
        border-color: #2d5a87;
        box-shadow: 0 4px 12px rgba(30, 58, 95, 0.15);
        transform: translateY(-1px);
    }

    .result-card .title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }

    .result-card .meta {
        display: flex;
        gap: 1rem;
        font-size: 0.85rem;
        color: #6b7280;
    }

    .result-card .citation {
        background: #f3f4f6;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.8rem;
    }

    .result-card .preview {
        margin-top: 0.75rem;
        font-size: 0.9rem;
        color: #4b5563;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* View button */
    .view-btn {
        display: inline-block;
        background: #1e3a5f;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.75rem;
        transition: background 0.2s;
    }

    .view-btn:hover {
        background: #2d5a87;
        color: white !important;
    }

    /* Detail page styles */
    .detail-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }

    .detail-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
        color: white;
        line-height: 1.3;
    }

    .detail-header .breadcrumb {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-bottom: 0.75rem;
    }

    .meta-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .meta-card .label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }

    .meta-card .value {
        font-size: 1rem;
        color: #1f2937;
        font-weight: 500;
    }

    .law-text-container {
        background: #fafbfc;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 2rem;
        line-height: 1.8;
        font-size: 1rem;
        color: #374151;
    }

    /* Pagination */
    .pagination-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin: 1.5rem 0;
    }

    .page-info {
        background: #f3f4f6;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #4b5563;
    }

    /* Back button */
    .back-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #1e3a5f;
        font-weight: 500;
        margin-bottom: 1rem;
        cursor: pointer;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #f8fafc;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label {
        font-weight: 600;
        color: #1f2937;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Improve button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        border-color: #1e3a5f;
        color: #1e3a5f;
    }

    /* Search results count */
    .results-info {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #1e40af;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


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
def get_total_count(_supabase: Client, states: tuple[str, ...], search_term: str = "") -> int:
    """Get total count of law_text rows for selected states."""
    query = (_supabase.table(TABLE_NAME)
             .select("id", count="exact")
             .eq("type", "law_text")
             .in_("state", list(states)))

    if search_term:
        query = query.ilike("properties->>law_text", f"%{search_term}%")

    response = query.execute()
    return response.count or 0


@st.cache_data(ttl=600)
def fetch_law_texts(_supabase: Client, states: tuple[str, ...], offset: int = 0, limit: int = PAGE_SIZE, search_term: str = "") -> pd.DataFrame:
    """Fetch paginated law_text rows for selected states."""
    query = (_supabase.table(TABLE_NAME)
             .select("id, properties, state")
             .eq("type", "law_text")
             .in_("state", list(states)))

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
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">404</div>
            <h2>Law Not Found</h2>
            <p style="color: #6b7280;">The requested statute could not be found in the database.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Back to Browse"):
            st.query_params.clear()
            st.rerun()
        return

    # Back button
    if st.button("← Back to Browse"):
        st.query_params.clear()
        st.rerun()

    # Detail header with title
    state_display = law['state'].replace('_', ' ').title()
    title = law["title"] or "Untitled Section"

    st.markdown(f"""
    <div class="detail-header">
        <div class="breadcrumb">{state_display} Statutes</div>
        <h1>{title}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Metadata cards row
    meta_cols = []
    if law.get("citation"):
        meta_cols.append(("Citation", law["citation"]))
    meta_cols.append(("State", state_display))
    if law.get("url"):
        meta_cols.append(("Source", f'<a href="{law["url"]}" target="_blank" style="color: #1e3a5f;">View Original</a>'))

    cols = st.columns(len(meta_cols))
    for i, (label, value) in enumerate(meta_cols):
        with cols[i]:
            st.markdown(f"""
            <div class="meta-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Law text section
    st.markdown("### Full Text")
    law_text = law["law_text"]
    if law_text:
        # Escape HTML and format newlines
        escaped_text = html.escape(law_text)
        formatted_text = escaped_text.replace('\n', '<br>')

        st.markdown(
            f"""<div class="law-text-container">
                {formatted_text}
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f9fafb; border-radius: 10px; color: #6b7280;">
            <p>No law text available for this statute.</p>
        </div>
        """, unsafe_allow_html=True)


def show_browse_page(supabase: Client):
    """Display the main browse page."""

    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = 0

    # Sidebar - State selection
    st.sidebar.markdown("### Filters")

    with st.spinner("Loading states..."):
        states = fetch_states(supabase)

    if not states:
        st.warning("No states found in the database.")
        return

    # Format state names for display
    state_display = {s: s.replace("_", " ").title() for s in states}

    # Multi-select for states with Select All option
    st.sidebar.checkbox(
        "Select All States",
        key="select_all_states",
        on_change=lambda: setattr(st.session_state, 'page', 0)
    )

    if st.session_state.get("select_all_states", False):
        selected_states = states
        st.sidebar.multiselect(
            "Selected States",
            options=states,
            default=states,
            format_func=lambda x: state_display[x],
            disabled=True,
            key="states_display_disabled"
        )
    else:
        selected_states = st.sidebar.multiselect(
            "Select States",
            options=states,
            default=[states[0]] if states else [],
            format_func=lambda x: state_display[x],
            on_change=lambda: setattr(st.session_state, 'page', 0)
        )

    if not selected_states:
        st.warning("Please select at least one state from the sidebar.")
        return

    # Convert to tuple for caching (lists aren't hashable)
    selected_states_tuple = tuple(selected_states)

    # Search filter (server-side)
    search_term = st.sidebar.text_input(
        "Search in law texts",
        placeholder="Enter search term...",
        on_change=lambda: setattr(st.session_state, 'page', 0)
    )

    # Get total count
    total_count = get_total_count(supabase, selected_states_tuple, search_term)
    total_pages = max(1, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)

    # Build subtitle based on selection
    if len(selected_states) == len(states):
        states_subtitle = "All States"
    elif len(selected_states) == 1:
        states_subtitle = state_display[selected_states[0]]
    elif len(selected_states) <= 3:
        states_subtitle = ", ".join(state_display[s] for s in selected_states)
    else:
        states_subtitle = f"{len(selected_states)} States Selected"

    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>State Statutes Browser</h1>
        <p>{states_subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

    if total_count == 0:
        st.warning(f"No law texts found for the selected states.")
        return

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{len(selected_states):,}</div>
            <div class="label">States</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{total_count:,}</div>
            <div class="label">Total Statutes</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{total_pages:,}</div>
            <div class="label">Pages</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{PAGE_SIZE}</div>
            <div class="label">Per Page</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pagination controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("« First", disabled=st.session_state.page == 0, use_container_width=True):
            st.session_state.page = 0
            st.rerun()

    with col2:
        if st.button("‹ Prev", disabled=st.session_state.page == 0, use_container_width=True):
            st.session_state.page -= 1
            st.rerun()

    with col3:
        st.markdown(f"""
        <div class="page-info" style="text-align: center;">
            Page <strong>{st.session_state.page + 1}</strong> of <strong>{total_pages}</strong>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        if st.button("Next ›", disabled=st.session_state.page >= total_pages - 1, use_container_width=True):
            st.session_state.page += 1
            st.rerun()

    with col5:
        if st.button("Last »", disabled=st.session_state.page >= total_pages - 1, use_container_width=True):
            st.session_state.page = total_pages - 1
            st.rerun()

    # Fetch current page of data
    offset = st.session_state.page * PAGE_SIZE
    with st.spinner("Loading law texts..."):
        df = fetch_law_texts(supabase, selected_states_tuple, offset, PAGE_SIZE, search_term)

    # Show range info
    start_row = offset + 1
    end_row = min(offset + PAGE_SIZE, total_count)

    if search_term:
        st.markdown(f"""
        <div class="results-info">
            Showing results {start_row:,} - {end_row:,} of {total_count:,} matching "<strong>{search_term}</strong>"
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="results-info">
            Showing results {start_row:,} - {end_row:,} of {total_count:,}
        </div>
        """, unsafe_allow_html=True)

    # Display results as cards
    for _, row in df.iterrows():
        title = row["title"] or "Untitled Section"
        citation = row.get("citation", "")
        preview = row.get("law_text", "")[:200] + "..." if row.get("law_text") and len(row.get("law_text", "")) > 200 else row.get("law_text", "")

        citation_html = f'<span class="citation">{citation}</span>' if citation else ''

        st.markdown(f"""
        <div class="result-card">
            <div class="title">{title}</div>
            <div class="meta">{citation_html}</div>
            <div class="preview">{preview}</div>
            <a href="?id={row['id']}" class="view-btn">View Full Text</a>
        </div>
        """, unsafe_allow_html=True)


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
