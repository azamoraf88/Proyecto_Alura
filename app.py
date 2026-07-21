import os
import tempfile
from pathlib import Path

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

st.set_page_config(page_title="IngrediBot", page_icon="📄", layout="wide")
st.title("Hola! Soy IngrediBot, un especialista en los procedimientos de la empresa Ingreditech S. de R.L. de C.V.")
st.caption("Para que pueda contestar tus preguntas, sube los procedimientos en PDF que deseas conocer mejor :).")

PERSIST_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "pdf_documents"


@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


@st.cache_resource
def get_llm(groq_api_key: str):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
    )


def init_vector_store(embeddings):
    PERSIST_DIR.mkdir(exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
    )


def load_documents_from_uploads(uploaded_files):
    documents: list[Document] = []
    temp_paths = []

    try:
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_paths.append(tmp_file.name)

        for temp_path in temp_paths:
            loader = PyPDFLoader(temp_path)
            documents.extend(loader.load())
    finally:
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return documents


def index_documents(uploaded_files):
    if not uploaded_files:
        st.warning("Sube al menos un archivo PDF para comenzar.")
        return None

    if not st.session_state.get("groq_api_key"):
        st.warning("Introduce tu API key de Groq antes de procesar los documentos.")
        return None

    embeddings = get_embeddings()
    docs = load_documents_from_uploads(uploaded_files)
    if not docs:
        st.warning("No se pudieron leer documentos desde los PDFs cargados.")
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    if st.session_state.get("vector_store") is None:
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(PERSIST_DIR),
            collection_name=COLLECTION_NAME,
        )
    else:
        vector_store = st.session_state.vector_store
        vector_store.add_documents(chunks)
        vector_store.persist()

    st.session_state.vector_store = vector_store
    st.session_state.documents_indexed = True
    st.success(f"Se procesaron {len(chunks)} fragmentos de {len(uploaded_files)} PDF(s).")
    return vector_store


def answer_question(question: str):
    if not st.session_state.get("groq_api_key"):
        return "Introduce tu API key de Groq para poder responder preguntas.", []

    vector_store = st.session_state.get("vector_store")
    if vector_store is None:
        return "Aún no hay documentos indexados. Sube un archivo antes de comenzar.", []

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    if hasattr(retriever, "invoke"):
        docs = retriever.invoke(question)
    else:
        docs = retriever.get_relevant_documents(question)

    if not docs:
        return "No hay información disponible en los documentos cargados. Intenta cargando otro documento o haciendo otra pregunta.", []

    llm = get_llm(st.session_state.groq_api_key)
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = (
        "Eres el jefe de calidad de una empresa certificada en FSSC 22000. Debes responder preguntas sobre los procedimientos de la empresa. Responde en español. Usa únicamente la información del contexto proporcionado. "
        "Si el contexto no contiene una respuesta clara, responde exactamente: "
        "'La información no se encuentra en los documentos cargados.'\n\n"
        f"Contexto:\n{context}\n\nPregunta: {question}"
    )

    response = llm.invoke(prompt)
    answer = response.content.strip() if hasattr(response, "content") else str(response).strip()

    if not answer or answer.lower() == "none":
        return "No hay información disponible en los documentos cargados. Intenta cargando otro documento o haciendo otra pregunta.", []

    sources = []
    for doc in docs:
        source_name = getattr(doc.metadata, "get", lambda *_args, **_kwargs: "Documento")("source")
        if isinstance(source_name, str) and source_name:
            sources.append(source_name)
        else:
            sources.append("Documento cargado con éxito, ya puedes comenzar a hacer preguntas sobre su contenido.")

    return answer, list(dict.fromkeys(sources))


if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "documents_indexed" not in st.session_state:
    st.session_state.documents_indexed = False

with st.sidebar:
    st.header("Configuración")
    st.session_state.groq_api_key = st.text_input(
        "API key de Groq",
        type="password",
        value=st.session_state.get("groq_api_key", ""),
        help="Inserta tu clave para usar Groq como modelo de lenguaje.",
    )
    if st.session_state.groq_api_key:
        os.environ["GROQ_API_KEY"] = st.session_state.groq_api_key

    st.divider()
    st.subheader("1) Cargar documentos PDF")
    uploaded_files = st.file_uploader(
        "Selecciona uno o varios PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("Guardar documentos en la base vectorial", use_container_width=True):
        with st.spinner("Procesando y guardando los PDFs..."):
            index_documents(uploaded_files)

    if st.session_state.documents_indexed:
        st.success("Los documentos ya están disponibles para consultar.")

st.subheader("2) Chat sobre los documentos")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe una pregunta sobre los documentos..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando respuesta..."):
            response, sources = answer_question(prompt)
        st.markdown(response)
        if sources:
            with st.expander("Fuentes utilizadas"):
                for source in sources:
                    st.write(f"- {source}")
    st.session_state.messages.append({"role": "assistant", "content": response})
