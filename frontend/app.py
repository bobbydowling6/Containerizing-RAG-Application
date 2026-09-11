import streamlit as st
import requests
import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Assistant", page_icon="🤖", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 RAG Assistant")
    try:
        health = requests.get(f"{API_URL}/health", timeout=3).json()
        st.success(f"API: Connected")
        st.write(f"Gemini: {health.get('gemini', 'unknown')}")
        st.metric("Documents", health.get('documents', 0))
    except:
        st.error("API not available")

    if st.button("🔄 Re-index Documents"):
        try:
            r = requests.post(f"{API_URL}/ingest", timeout=30)
            if r.status_code == 200:
                data = r.json()
                st.success(data.get("message", "Done"))
                st.rerun()
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Ingestion failed: {str(e)}")

# --- Chat Interface ---
st.title("Ask Your Documents")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.caption(f"{s['source']} (distance: {s['distance']:.3f})")

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(f"{API_URL}/ask", json={"question": prompt}, timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    st.write(data["answer"])

                    sources = data.get("sources", [])
                    if sources:
                        with st.expander(f"Sources ({data.get('confidence', 'unknown')} confidence)"):
                            for s in sources:
                                st.caption(f"{s['source']} (dist: {s['distance']:.3f})")
                                st.write(s['text'][:200] + "...")

                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": sources
                    })
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
