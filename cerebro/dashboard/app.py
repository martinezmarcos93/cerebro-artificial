"""
Dashboard de Observabilidad — Cerebro Artificial.
Ejecutar con: streamlit run cerebro/dashboard/app.py
"""
import sys
import os
import json
from pathlib import Path
from collections import Counter

ROOT = str(Path(__file__).parent.parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

st.set_page_config(
    page_title="Cerebro Artificial",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("🧠 Cerebro Artificial")
vault_path = st.sidebar.text_input("Vault path", value="vault")

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
if auto_refresh:
    intervalo = st.sidebar.radio(
        "Intervalo",
        ["30 segundos", "1 minuto", "5 minutos"],
        index=1,
    )
    _seg = {"30 segundos": 30, "1 minuto": 60, "5 minutos": 300}[intervalo]
    import time
    time.sleep(_seg)
    st.rerun()

st.sidebar.markdown("---")
vista = st.sidebar.radio(
    "Vista",
    ["Resumen", "Neuronas", "Grafo de Conocimiento", "Log del Yo", "Arquetipos"],
)

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------

@st.cache_data(ttl=5)
def cargar_datos(vault):
    from cerebro.rag.indexador import Indexador
    idx = Indexador(vault)
    idx.indexar()
    return idx


@st.cache_data(ttl=5)
def leer_log(vault):
    log_file = os.path.join(vault, ".yo_log.jsonl")
    if not os.path.exists(log_file):
        return []
    entradas = []
    with open(log_file, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                try:
                    entradas.append(json.loads(linea))
                except Exception:
                    pass
    return entradas


try:
    idx = cargar_datos(vault_path)
    neuronas = list(idx._neuronas.values())
except Exception as exc:
    st.error(f"No se pudo cargar el vault '{vault_path}': {exc}")
    st.stop()

# ---------------------------------------------------------------------------
# Vista: Resumen
# ---------------------------------------------------------------------------
if vista == "Resumen":
    st.title("Resumen del Cerebro")

    total = len(neuronas)
    tipos = Counter(n.post.metadata.get("tipo", "?") for n in neuronas)
    arquetipos = Counter(
        n.post.metadata.get("arquetipo_vinculado", "").replace("[[", "").replace(".md]]", "")
        for n in neuronas
        if n.post.metadata.get("arquetipo_vinculado")
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Neuronas totales", total)
    col2.metric("Conflictos", tipos.get("conflicto", 0))
    col3.metric("Nodos en grafo", idx.grafo.number_of_nodes())
    col4.metric("Edges en grafo", idx.grafo.number_of_edges())

    st.subheader("Distribución por tipo")
    if tipos:
        import pandas as pd
        df_tipos = pd.DataFrame(list(tipos.items()), columns=["Tipo", "Cantidad"])
        st.bar_chart(df_tipos.set_index("Tipo"))

    st.subheader("Etapa actual estimada")
    if total == 0:
        etapa = "Sin datos"
    elif tipos.get("regla", 0) >= 1:
        etapa = "Operaciones Formales"
    elif tipos.get("concepto", 0) >= 1:
        etapa = "Operaciones Concretas"
    elif tipos.get("simbolo", 0) >= 1:
        etapa = "Preoperacional"
    else:
        etapa = "Sensoriomotora"
    st.info(f"**{etapa}** — basado en los tipos de neuronas presentes en el vault.")

# ---------------------------------------------------------------------------
# Vista: Neuronas
# ---------------------------------------------------------------------------
elif vista == "Neuronas":
    st.title("Explorador de Neuronas")

    import pandas as pd
    filas = []
    for n in neuronas:
        m = n.post.metadata
        filas.append({
            "Significante": m.get("significante", "?"),
            "Tipo": m.get("tipo", "?"),
            "Energia": round(float(m.get("estado_energetico", 0)), 2),
            "Arquetipo": m.get("arquetipo_vinculado", "").replace("[[", "").replace(".md]]", ""),
            "Etapa": m.get("etapa_creacion", "?"),
            "ID": m.get("id", "?"),
        })

    df = pd.DataFrame(filas)

    tipos_disponibles = ["Todos"] + sorted(df["Tipo"].unique().tolist())
    tipo_filtro = st.selectbox("Filtrar por tipo", tipos_disponibles)
    if tipo_filtro != "Todos":
        df = df[df["Tipo"] == tipo_filtro]

    st.dataframe(df, use_container_width=True)

    if st.checkbox("Ver contenido de una neurona"):
        sig_sel = st.selectbox("Neurona", [n.post.metadata.get("significante", "?") for n in neuronas])
        neurona_sel = next(
            (n for n in neuronas if n.post.metadata.get("significante") == sig_sel), None
        )
        if neurona_sel:
            st.json(neurona_sel.post.metadata)
            st.markdown(neurona_sel.post.content or "*Sin contenido*")

# ---------------------------------------------------------------------------
# Vista: Grafo de Conocimiento
# ---------------------------------------------------------------------------
elif vista == "Grafo de Conocimiento":
    st.title("Grafo de Conocimiento")

    try:
        import matplotlib.pyplot as plt
        import networkx as nx

        G = idx.grafo
        if G.number_of_nodes() == 0:
            st.warning("El grafo está vacío. Envía algunos estímulos primero.")
        else:
            fig, ax = plt.subplots(figsize=(12, 8))
            pos = nx.spring_layout(G, seed=42, k=2)

            color_map = {
                "esquema_sensoriomotor": "#4FC3F7",
                "simbolo": "#81C784",
                "concepto": "#FFB74D",
                "conflicto": "#E57373",
                "regla": "#BA68C8",
                "arquetipo": "#F06292",
            }

            node_colors = []
            for node in G.nodes():
                neurona_node = next(
                    (n for n in neuronas if n.post.metadata.get("significante") == node), None
                )
                tipo = neurona_node.post.metadata.get("tipo", "?") if neurona_node else "?"
                node_colors.append(color_map.get(tipo, "#B0BEC5"))

            nx.draw(
                G, pos, ax=ax,
                node_color=node_colors,
                with_labels=True,
                node_size=800,
                font_size=7,
                font_weight="bold",
                edge_color="#90A4AE",
                arrows=True,
                arrowsize=10,
            )

            leyenda = [
                plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=10, label=t)
                for t, c in color_map.items()
            ]
            ax.legend(handles=leyenda, loc="upper left", fontsize=8)
            ax.set_title("Grafo de conocimiento del vault", fontsize=12)
            st.pyplot(fig)
            plt.close(fig)

    except ImportError:
        st.error("matplotlib no está instalado. Ejecuta: pip install matplotlib")

# ---------------------------------------------------------------------------
# Vista: Log del Yo
# ---------------------------------------------------------------------------
elif vista == "Log del Yo":
    st.title("Decisiones del Yo")
    st.caption("Cada fila es una decision que el Yo tomó: enlazar o crear conflicto.")

    entradas = leer_log(vault_path)
    if not entradas:
        st.info("El log está vacío. Genera interacciones para ver las decisiones del Yo.")
    else:
        import pandas as pd
        df_log = pd.DataFrame(entradas)
        df_log = df_log.rename(columns={
            "ts": "Timestamp",
            "tipo": "Tipo",
            "origen": "Origen",
            "destino": "Destino",
            "resultado": "Resultado",
            "razon": "Razón",
        })

        col_tipo = st.selectbox("Filtrar por tipo", ["Todos", "enlace", "conflicto"])
        if col_tipo != "Todos":
            df_log = df_log[df_log["Tipo"] == col_tipo]

        st.dataframe(df_log[::-1].reset_index(drop=True), use_container_width=True)

        col1, col2 = st.columns(2)
        total_log = len(entradas)
        enlaces = sum(1 for e in entradas if e.get("tipo") == "enlace")
        conflictos_log = sum(1 for e in entradas if e.get("tipo") == "conflicto")
        col1.metric("Total de decisiones", total_log)
        col2.metric("Ratio conflicto/enlace",
                    f"{conflictos_log}/{enlaces}" if enlaces else f"{conflictos_log}/0")

# ---------------------------------------------------------------------------
# Vista: Arquetipos
# ---------------------------------------------------------------------------
elif vista == "Arquetipos":
    st.title("Distribución de Arquetipos")

    arquetipos = Counter(
        n.post.metadata.get("arquetipo_vinculado", "").replace("[[", "").replace(".md]]", "")
        for n in neuronas
        if n.post.metadata.get("arquetipo_vinculado")
    )

    if not arquetipos:
        st.info("Ninguna neurona tiene arquetipo_vinculado aún. "
                "El motor junguiano actúa desde la etapa Preoperacional en adelante.")
    else:
        import pandas as pd
        df_arq = pd.DataFrame(list(arquetipos.items()), columns=["Arquetipo", "Neuronas"])
        st.bar_chart(df_arq.set_index("Arquetipo"))
        st.dataframe(df_arq.sort_values("Neuronas", ascending=False), use_container_width=True)

        st.subheader("Neuronas por arquetipo")
        arq_sel = st.selectbox("Arquetipo", list(arquetipos.keys()))
        patron = f"[[{arq_sel}.md]]"
        filtradas = [
            n for n in neuronas
            if n.post.metadata.get("arquetipo_vinculado") == patron
        ]
        for n in filtradas:
            sig = n.post.metadata.get("significante", "?")
            tipo = n.post.metadata.get("tipo", "?")
            energia = n.post.metadata.get("estado_energetico", 0)
            st.markdown(f"- **{sig}** *(tipo: {tipo}, energia: {energia:.2f})*")
