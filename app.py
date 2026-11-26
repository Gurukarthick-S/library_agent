"""Streamlit page. Every visitor pastes their own free Gemini key; nothing is stored."""
import streamlit as st

import graph_core
import rag_core

st.set_page_config(page_title="Campus Library Helper", page_icon="📚")
st.title("📚 Campus Library Helper")
st.caption(f"Ask about {graph_core.TOPIC}. Answers come from the documents, with sources.")

with st.sidebar:
    api_key = st.text_input("Your Gemini API key", type="password",
                            help="Get a free key at aistudio.google.com. It is used only in your session.")
    st.markdown("[Get a free key](https://aistudio.google.com)")
    if st.button("Clear chat"):
        st.session_state.history = []
        st.session_state.shown = []
        st.rerun()

st.session_state.setdefault("history", [])   # sent to the rewrite step
st.session_state.setdefault("shown", [])     # what the page displays

if not api_key:
    st.info("Paste your Gemini key in the sidebar to start.")
    st.stop()

if st.session_state.get("key_used") != api_key:
    try:
        with st.spinner("Indexing the documents..."):
            store = rag_core.build_store(api_key)
        st.session_state.graph = graph_core.build_graph(graph_core.make_llm(api_key), store)
        st.session_state.key_used = api_key
    except Exception as exc:
        st.error(f"Could not index the documents. Check your key and try again. ({exc})")
        st.stop()


def show_extras(item):
    st.caption(f"Route: **{item['route']}**   |   Path: {item['path']}")
    if item["sources"]:
        with st.expander("Sources"):
            for p in item["sources"]:
                st.markdown(f"**[{p['n']}] {p['source']}**")
                st.write(p["text"])
    if item["steps"]:
        with st.expander("Agent steps"):
            for s in item["steps"]:
                st.write(s)


for msg in st.session_state.shown:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            show_extras(msg)

question = st.chat_input("Ask a question or give a task...")
if question:
    st.session_state.shown.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = graph_core.run_turn(st.session_state.graph, st.session_state.history, question)
        except Exception as exc:
            result = {"answer": f"Something went wrong: {exc}", "route": "error",
                      "path": "", "sources": [], "steps": []}
        st.write(result["answer"])
        show_extras(result)
    st.session_state.history += [
        {"role": "user", "content": question},
        {"role": "assistant", "content": result["answer"]},
    ]
    st.session_state.shown.append({"role": "assistant", "content": result["answer"], **result})
