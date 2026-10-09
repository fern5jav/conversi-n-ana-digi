import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Laboratorio interactivo de señales", page_icon="〰️", layout="wide")

BG = "#0b1220"
PANEL = "#121e30"
FG = "#edf4ff"
MUTED = "#9eb0c9"
CYAN = "#45caff"
ORANGE = "#ffad5c"
GREEN = "#45e0a0"
PURPLE = "#b6a0ff"
GRID = "#2c3e57"

st.markdown("""
<style>
.stApp { background: #0b1220; color: #edf4ff; }
[data-testid="stHeader"] { background: rgba(11,18,32,0.95); }
section[data-testid="stSidebar"] { background: #121e30; }
h1,h2,h3,p,label,span { color: #edf4ff; }
div[data-testid="stMetric"] { background:#121e30; border:1px solid #2c3e57; padding:14px; border-radius:12px; }
.stButton button { border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

def signal_function(t):
    return 0.72*np.sin(2*np.pi*2*t) + 0.20*np.sin(2*np.pi*5*t)

def style_fig(fig, height=380):
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=PANEL, font=dict(color=FG),
        margin=dict(l=35,r=20,t=55,b=40), height=height,
        legend=dict(bgcolor=PANEL, bordercolor=GRID),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID)
    )
    return fig

st.title("〰️ LABORATORIO INTERACTIVO DE SEÑALES")
st.caption("Observa paso a paso cómo una señal se digitaliza, se reconstruye y se transmite.")
st.markdown("---")

tab_adc, tab_codes, tab_mod = st.tabs(["① ADC / DAC", "② Codificación de línea", "③ Modulación digital"])

with tab_adc:
    st.subheader("Conversión analógico-digital y reconstrucción")
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        fs = st.slider("Frecuencia de muestreo (Hz)", 8, 100, 24, step=4)
    with col2:
        bits = st.slider("Resolución (bits)", 1, 8, 3)
    with col3:
        stage = st.radio("Etapa de la demostración", ["Señal original", "Muestreo", "Cuantización", "Reconstrucción DAC"], horizontal=True)
    t = np.linspace(0,1,1800,endpoint=False)
    original = signal_function(t)
    tm = np.arange(0,1,1/fs)
    samples = signal_function(tm)
    levels = 2**bits
    idx = np.clip(np.round((samples+1)/2*(levels-1)),0,levels-1).astype(int)
    quantized = -1 + idx*2/(levels-1)
    reconstructed = np.interp(t,tm,quantized)
    mse = float(np.mean((original-reconstructed)**2))
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Muestras por segundo", f"{fs} Hz")
    m2.metric("Resolución", f"{bits} bits")
    m3.metric("Niveles de cuantización", str(levels))
    m4.metric("Error cuadrático medio", f"{mse:.4f}")
    phase = ["Señal original","Muestreo","Cuantización","Reconstrucción DAC"].index(stage)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=.12,
                        subplot_titles=("ETAPA 1 · Señal analógica original","ETAPA 2 · Muestreo y cuantización","ETAPA 3 · Reconstrucción D/A"))
    fig.add_trace(go.Scatter(x=t,y=original,mode="lines",name="Señal original",line=dict(color=CYAN,width=2.5)),row=1,col=1)
    fig.add_trace(go.Scatter(x=t,y=original,mode="lines",name="Referencia",line=dict(color=CYAN,width=1,dash="dot"),opacity=.25,showlegend=False),row=2,col=1)
    if phase >= 1:
        fig.add_trace(go.Scatter(x=tm,y=samples,mode="lines+markers",name="Muestras",line=dict(color=ORANGE,width=1.5),marker=dict(size=6)),row=2,col=1)
    if phase >= 2:
        fig.add_trace(go.Scatter(x=tm,y=quantized,mode="lines",line=dict(color=GREEN,width=2.5,shape="hv"),name="Cuantizada"),row=2,col=1)
    fig.add_trace(go.Scatter(x=t,y=original,mode="lines",name="Original",line=dict(color=CYAN,width=1.4),opacity=.35),row=3,col=1)
    if phase >= 3:
        fig.add_trace(go.Scatter(x=t,y=reconstructed,mode="lines",name="Reconstruida",line=dict(color=GREEN,width=2.5)),row=3,col=1)
    fig.update_xaxes(title_text="Tiempo (s)",range=[0,1])
    fig.update_yaxes(range=[-1.15,1.15],title_text="Amplitud")
    style_fig(fig, 760)
    st.plotly_chart(fig,use_container_width=True)
    st.info(f"Etapa seleccionada: **{stage}**. Cambia los parámetros y la etapa para observar cómo varía la conversión.")

with tab_codes:
    st.subheader("Codificación de línea")
    c1,c2 = st.columns([2,1])
    with c1:
        raw = st.text_input("Secuencia binaria (de 1 a 40 bits)", "10110010", key="code_bits").strip()
    with c2:
        code_type = st.selectbox("Técnica", ["Todas","NRZ-L","RZ unipolar","Manchester","AMI bipolar"])
    if not raw or len(raw)>40 or any(c not in "01" for c in raw):
        st.error("Escribe de 1 a 40 bits usando solamente 0 y 1.")
    else:
        bitlist = [int(c) for c in raw]
        codes={}
        codes["NRZ-L"] = np.repeat(np.where(np.array(bitlist)==1,1,-1),100)
        rz,man,ami,last=[],[],[],-1
        for b in bitlist:
            rz.extend(([1]*50+[0]*50) if b else ([0]*100))
            man.extend(([1]*50+[-1]*50) if b else ([-1]*50+[1]*50))
            if b:
                last *= -1
                ami.extend([last]*100)
            else:
                ami.extend([0]*100)
        codes["RZ unipolar"]=np.array(rz)
        codes["Manchester"]=np.array(man)
        codes["AMI bipolar"]=np.array(ami)
        names=list(codes) if code_type=="Todas" else [code_type]
        fig=make_subplots(rows=len(names),cols=1,shared_xaxes=True,vertical_spacing=.08,subplot_titles=names)
        x=np.arange(len(bitlist)*100)/100
        for i,name in enumerate(names,1):
            fig.add_trace(go.Scatter(x=x,y=codes[name],mode="lines",line=dict(color=CYAN,width=2.5,shape="hv"),name=name,showlegend=False),row=i,col=1)
            fig.update_yaxes(range=[-1.4,1.4],title_text="Nivel",row=i,col=1)
            for j,b in enumerate(bitlist):
                fig.add_annotation(x=j+.5,y=1.18,text=str(b),showarrow=False,font=dict(color=ORANGE,size=12),row=i,col=1)
        fig.update_xaxes(title_text="Tiempo (intervalos de bit)",range=[0,len(bitlist)])
        style_fig(fig,max(380,180*len(names)))
        st.plotly_chart(fig,use_container_width=True)
        st.caption("Cada técnica representa los bits mediante distintos niveles eléctricos y transiciones.")

with tab_mod:
    st.subheader("Modulación digital")
    c1,c2=st.columns([2,1])
    with c1:
        rawm=st.text_input("Secuencia binaria (de 1 a 40 bits)","10110010",key="mod_bits").strip()
    with c2:
        kind=st.selectbox("Tipo de modulación",["ASK","FSK","BPSK"])
    if not rawm or len(rawm)>40 or any(c not in "01" for c in rawm):
        st.error("Escribe de 1 a 40 bits usando solamente 0 y 1.")
    else:
        bbits=np.array([int(c) for c in rawm])
        spb=400
        x=np.arange(len(bbits)*spb)/spb
        b=bbits[np.minimum(x.astype(int),len(bbits)-1)]
        f0,f1=4,7
        if kind=="ASK":
            y=np.where(b==1,1.0,.22)*np.sin(2*np.pi*f0*x)
        elif kind=="FSK":
            y=np.sin(2*np.pi*np.where(b==1,f1,f0)*x)
        else:
            y=np.sin(2*np.pi*f0*x+np.where(b==1,0,np.pi))
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines",line=dict(color=GREEN,width=1.8),name=f"Señal {kind}"))
        for i,bit in enumerate(bbits):
            fig.add_annotation(x=i+.5,y=1.18,text=str(bit),showarrow=False,font=dict(color=ORANGE,size=13))
        fig.update_layout(title=f"{kind} · Señal modulada para {rawm}",xaxis_title="Tiempo (intervalos de bit)",yaxis_title="Amplitud")
        fig.update_xaxes(range=[0,len(bbits)],dtick=1)
        fig.update_yaxes(range=[-1.4,1.4])
        style_fig(fig,470)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("**Interpretación rápida**")
        if kind=="ASK":
            st.write("ASK cambia la amplitud de la portadora según el bit transmitido.")
        elif kind=="FSK":
            st.write("FSK representa los bits mediante diferentes frecuencias.")
        else:
            st.write("BPSK representa los bits cambiando la fase de la portadora.")

st.markdown("---")
st.caption("Simulación educativa por software · No requiere hardware ADC/DAC")
