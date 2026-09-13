import streamlit as st

from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .step-card {
        padding: 1rem;
        border-radius: 12px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }

    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🔎 AI Research Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Search → Read → Write → Criticize — automated research pipeline'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    max_search_chars = st.slider(
        "Search context",
        min_value=1000,
        max_value=20000,
        value=10000,
        step=1000,
    )

    show_intermediate = st.checkbox(
        "Show intermediate results",
        value=True,
    )

    st.divider()

    st.caption("AI Research Pipeline")
    st.caption("Search → Reader → Writer → Critic")


# ============================================================
# USER INPUT
# ============================================================

st.subheader("What do you want to research?")

topic = st.text_area(
    "Research topic",
    placeholder=(
        "Example: "
        "Impact of artificial intelligence on education in Bangladesh"
    ),
    height=120,
    label_visibility="collapsed",
)


run_button = st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True,
)


# ============================================================
# PIPELINE
# ============================================================

if run_button:

    if not topic.strip():
        st.warning("⚠️ Please enter a research topic first.")
        st.stop()

    # --------------------------------------------------------
    # CREATE STATE
    # --------------------------------------------------------

    state = {
        "topic": topic,
        "search_results": "",
        "scraped_content": "",
        "report": "",
        "feedback": "",
        "final_report": "",
    }

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    progress = st.progress(0)

    status = st.empty()

    # ========================================================
    # STEP 1 — SEARCH
    # ========================================================

    status.info("🔎 Step 1/4 — Searching for reliable sources...")

    with st.spinner("Search agent is working..."):

        try:

            search_agent = build_search_agent()

            search_result = search_agent.invoke(
                {
                    "messages": [
                        (
                            "user",
                            f"""
Find recent, reliable and detailed information about:

{topic}

Return relevant sources and URLs.
""",
                        )
                    ]
                }
            )

            state["search_results"] = (
                search_result["messages"][-1].content
            )

            progress.progress(25)

        except Exception as e:

            st.error(f"❌ Search agent failed: {e}")
            st.stop()

    # ========================================================
    # STEP 2 — READER
    # ========================================================

    status.info("📖 Step 2/4 — Reading the best sources...")

    with st.spinner("Reader agent is scraping the most relevant source..."):

        try:

            search_context = state["search_results"][:max_search_chars]

            reader_agent = build_reader_agent()

            reader_result = reader_agent.invoke(
                {
                    "messages": [
                        (
                            "user",
                            f"""
Based on the following search results about:

"{topic}"

Pick the most relevant and reliable URL and scrape it
for deeper content.

Search results:

{search_context}

Return the important factual information and source URL.
""",
                        )
                    ]
                }
            )

            state["scraped_content"] = (
                reader_result["messages"][-1].content
            )

            progress.progress(50)

        except Exception as e:

            st.error(f"❌ Reader agent failed: {e}")
            st.stop()

    # ========================================================
    # STEP 3 — WRITER
    # ========================================================

    status.info("✍️ Step 3/4 — Writing the research report...")

    with st.spinner("Writer is preparing the report..."):

        try:

            research_combined = f"""
SEARCH RESULTS:

{state["search_results"]}

DETAILED SCRAPED CONTENT:

{state["scraped_content"]}
"""

            report_result = writer_chain.invoke(
                {
                    "topic": topic,
                    "research": research_combined,
                }
            )

            if hasattr(report_result, "content"):
                state["report"] = report_result.content
            else:
                state["report"] = report_result

            progress.progress(75)

        except Exception as e:

            st.error(f"❌ Writer failed: {e}")
            st.stop()

    # ========================================================
    # STEP 4 — CRITIC
    # ========================================================

    status.info("🧐 Step 4/4 — Reviewing the report...")

    with st.spinner("Critic is reviewing the report..."):

        try:

            feedback_result = critic_chain.invoke(
                {
                    "report": state["report"]
                }
            )

            if hasattr(feedback_result, "content"):
                state["feedback"] = feedback_result.content
            else:
                state["feedback"] = feedback_result

            progress.progress(100)

        except Exception as e:

            st.error(f"❌ Critic failed: {e}")
            st.stop()

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    status.success("✅ Research completed successfully!")

    # Save state
    st.session_state["research_state"] = state


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "research_state" in st.session_state:

    state = st.session_state["research_state"]

    st.divider()

    st.subheader("📊 Research Results")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔎 Sources",
            "📖 Research",
            "📝 Report",
            "🧐 Critic",
        ]
    )

    # ========================================================
    # SOURCES
    # ========================================================

    with tab1:

        st.markdown("### 🔎 Search Results")

        st.markdown(state["search_results"])

    # ========================================================
    # SCRAPED CONTENT
    # ========================================================

    with tab2:

        st.markdown("### 📖 Detailed Research")

        st.markdown(state["scraped_content"])

    # ========================================================
    # REPORT
    # ========================================================

    with tab3:

        st.markdown("### 📝 Final Research Report")

        st.markdown(state["report"])

        st.download_button(
            label="⬇️ Download Report",
            data=state["report"],
            file_name="research_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ========================================================
    # CRITIC
    # ========================================================

    with tab4:

        st.markdown("### 🧐 Critic Feedback")

        st.markdown(state["feedback"])


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Research Assistant • Search → Reader → Writer → Critic"
)
