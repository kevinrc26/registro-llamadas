import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ============ CONFIGURACIÓN ============
st.set_page_config(
    page_title="Registro de Llamadas - Cooperativa",
    page_icon="📞",
    layout="wide"
)

st.title("📞 Cooperativa de Taxis - Registro de Llamadas")
st.markdown("---")

# ============ INICIALIZAR SESSION STATE ============
if 'editar_clicked' not in st.session_state:
    st.session_state.editar_clicked = False
if 'id_editar' not in st.session_state:
    st.session_state.id_editar = None
if 'buscar_input' not in st.session_state:
    st.session_state.buscar_input = ""
if 'registrar_clicked' not in st.session_state:
    st.session_state.registrar_clicked = False

# ============ BASE DE DATOS ============
def crear_bd():
    conn = sqlite3.connect('llamadas_web.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llamadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            cliente TEXT,
            medio TEXT,
            contacto TEXT,
            taxista TEXT,
            destino TEXT,
            estado TEXT,
            observaciones TEXT
        )
    ''')
    conn.commit()
    conn.close()

crear_bd()

# ============ FUNCIONES CRUD ============

# CREATE
def registrar_llamada(cliente, medio, contacto, taxista, destino, estado, observaciones):
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    
    conn = sqlite3.connect('llamadas_web.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO llamadas (fecha, hora, cliente, medio, contacto, taxista, destino, estado, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fecha, hora, cliente, medio, contacto, taxista, destino, estado, observaciones))
    conn.commit()
    conn.close()
    return True

# READ
def cargar_datos(buscar=""):
    conn = sqlite3.connect('llamadas_web.db')
    if buscar:
        df = pd.read_sql_query('''
            SELECT id, fecha, hora, cliente, medio, contacto, taxista, destino, estado, observaciones 
            FROM llamadas 
            WHERE cliente LIKE ? OR contacto LIKE ? OR taxista LIKE ? OR destino LIKE ?
            ORDER BY id DESC
        ''', conn, params=(f'%{buscar}%', f'%{buscar}%', f'%{buscar}%', f'%{buscar}%'))
    else:
        df = pd.read_sql_query('''
            SELECT id, fecha, hora, cliente, medio, contacto, taxista, destino, estado, observaciones 
            FROM llamadas 
            ORDER BY id DESC
        ''', conn)
    conn.close()
    return df

# UPDATE
def actualizar_llamada(id_registro, cliente, medio, contacto, taxista, destino, estado, observaciones):
    conn = sqlite3.connect('llamadas_web.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE llamadas 
        SET cliente=?, medio=?, contacto=?, taxista=?, destino=?, estado=?, observaciones=?
        WHERE id=?
    ''', (cliente, medio, contacto, taxista, destino, estado, observaciones, id_registro))
    conn.commit()
    conn.close()
    return True

# DELETE
def eliminar_llamada(id_registro):
    conn = sqlite3.connect('llamadas_web.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM llamadas WHERE id=?', (id_registro,))
    conn.commit()
    conn.close()
    return True

def obtener_llamada(id_registro):
    conn = sqlite3.connect('llamadas_web.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM llamadas WHERE id=?', (id_registro,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# ============ FORMULARIO CREATE ============
# Usar un formulario para capturar Enter
with st.form(key="registro_form", clear_on_submit=True):
    st.markdown("### ✏️ Registrar nueva llamada")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cliente = st.text_input("👤 Cliente *", placeholder="Nombre del cliente")
        medio = st.selectbox("📱 Medio", ["📞 Teléfono", "📱 WhatsApp", "💬 Messenger", "📲 Telegram", "Otro"])
    
    with col2:
        contacto = st.text_input("📞 Contacto *", placeholder="Teléfono o usuario")
        taxista = st.text_input("🚕 Taxista", placeholder="Nombre del taxista")
    
    with col3:
        destino = st.text_input("📍 Destino", placeholder="Lugar de destino")
        estado = st.selectbox("📌 Estado", ["⏳ Pendiente", "🚕 Asignado"])
    
    observaciones = st.text_area("📝 Observaciones", placeholder="Notas adicionales", height=80)
    
    # Botón Registrar dentro del formulario
    submitted = st.form_submit_button("✅ Registrar (Enter)", type="primary", use_container_width=True)
    
    if submitted:
        if not cliente or not contacto:
            st.error("⚠️ Cliente y Contacto son obligatorios")
        else:
            if registrar_llamada(cliente, medio, contacto, taxista, destino, estado, observaciones):
                st.success(f"✅ Llamada registrada: {cliente} - {contacto}")
                # El formulario con clear_on_submit=True ya limpia los campos
                st.rerun()

# ============ SEPARADOR ============
st.markdown("---")

# ============ BUSCADOR ============
col_buscar1, col_buscar2 = st.columns([3, 1])

with col_buscar1:
    buscar = st.text_input("🔍 Buscar llamadas", 
                           placeholder="Escribe nombre, contacto o taxista...", 
                           key="buscar_input")

with col_buscar2:
    st.write("")
    st.write("")
    if st.button("📋 Mostrar todos", use_container_width=True):
        st.session_state.buscar_input = ""
        st.rerun()

# ============ TABLA READ ============
st.subheader("📋 Historial de llamadas")

df = cargar_datos(st.session_state.buscar_input)

if df.empty:
    st.info("📭 No hay llamadas registradas aún")
else:
    st.dataframe(df[['id', 'fecha', 'hora', 'cliente', 'medio', 'contacto', 'taxista', 'destino', 'estado', 'observaciones']], 
                 use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        pendientes = len(df[df['estado'] == '⏳ Pendiente'])
        st.metric("⏳ Pendientes", pendientes)
    with col2:
        asignados = len(df[df['estado'] == '🚕 Asignado'])
        st.metric("🚕 Asignados", asignados)
    
    st.caption(f"📊 Total: {len(df)} llamadas")
    
    st.markdown("---")
    
    col_acc1, col_acc2, col_acc3 = st.columns(3)
    
    # 1. Exportar Excel
    with col_acc1:
        if st.button("📊 Exportar Excel", use_container_width=True):
            df_export = df[['id', 'fecha', 'hora', 'cliente', 'medio', 'contacto', 'taxista', 'destino', 'estado', 'observaciones']]
            df_export.to_excel("reporte_llamadas.xlsx", index=False)
            with open("reporte_llamadas.xlsx", "rb") as f:
                st.download_button(
                    label="📥 Descargar Excel",
                    data=f,
                    file_name=f"reporte_llamadas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    # 2. UPDATE - Editar
    with col_acc2:
        st.subheader("✏️ Editar llamada")
        opciones_editar = [f"ID {row['id']} - {row['cliente']}" for _, row in df.iterrows()]
        
        if opciones_editar:
            seleccion_editar = st.selectbox("Selecciona:", opciones_editar, key="editar_select")
            id_editar = int(seleccion_editar.split(" - ")[0].replace("ID ", ""))
            
            if st.button("✏️ Editar", use_container_width=True):
                st.session_state.id_editar = id_editar
                st.session_state.editar_clicked = True
                st.rerun()
    
    # 3. DELETE - Eliminar
    with col_acc3:
        st.subheader("🗑️ Eliminar llamada")
        opciones_eliminar = [f"ID {row['id']} - {row['cliente']}" for _, row in df.iterrows()]
        
        if opciones_eliminar:
            seleccion_eliminar = st.selectbox("Selecciona:", opciones_eliminar, key="eliminar_select")
            
            if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                id_eliminar = int(seleccion_eliminar.split(" - ")[0].replace("ID ", ""))
                try:
                    eliminar_llamada(id_eliminar)
                    st.success(f"✅ Llamada ID {id_eliminar} eliminada")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============ MODAL DE EDICIÓN ============
if st.session_state.editar_clicked and st.session_state.id_editar:
    st.markdown("---")
    st.subheader("✏️ Editar llamada")
    
    llamada = obtener_llamada(st.session_state.id_editar)
    
    if llamada:
        col_edit1, col_edit2, col_edit3 = st.columns(3)
        
        with col_edit1:
            nuevo_cliente = st.text_input("Cliente", value=llamada[3], key="edit_cliente")
            medio_opciones = ["📞 Teléfono", "📱 WhatsApp", "💬 Messenger", "📲 Telegram", "Otro"]
            medio_actual = llamada[4] if llamada[4] in medio_opciones else "📞 Teléfono"
            nuevo_medio = st.selectbox("Medio", medio_opciones, 
                                       index=medio_opciones.index(medio_actual),
                                       key="edit_medio")
        
        with col_edit2:
            nuevo_contacto = st.text_input("Contacto", value=llamada[5], key="edit_contacto")
            nuevo_taxista = st.text_input("Taxista", value=llamada[6] if llamada[6] else "", key="edit_taxista")
        
        with col_edit3:
            nuevo_destino = st.text_input("Destino", value=llamada[7] if llamada[7] else "", key="edit_destino")
            estado_actual = llamada[8] if llamada[8] in ["⏳ Pendiente", "🚕 Asignado"] else "⏳ Pendiente"
            nuevo_estado = st.selectbox("Estado", ["⏳ Pendiente", "🚕 Asignado"],
                                       index=0 if estado_actual == "⏳ Pendiente" else 1,
                                       key="edit_estado")
        
        nuevas_obs = st.text_area("Observaciones", value=llamada[9] if llamada[9] else "", height=80, key="edit_obs")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        with col_btn1:
            if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
                try:
                    actualizar_llamada(
                        st.session_state.id_editar,
                        nuevo_cliente,
                        nuevo_medio,
                        nuevo_contacto,
                        nuevo_taxista,
                        nuevo_destino,
                        nuevo_estado,
                        nuevas_obs
                    )
                    st.success(f"✅ Llamada ID {st.session_state.id_editar} actualizada")
                    st.session_state.editar_clicked = False
                    st.session_state.id_editar = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al actualizar: {str(e)}")
        
        with col_btn2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editar_clicked = False
                st.session_state.id_editar = None
                st.rerun()

# ============ PIE ============
st.markdown("---")
st.caption("📅 Datos guardados en llamadas_web.db | CRUD Completo | Presiona Enter para guardar | v1.0.0")