import streamlit as st
import pandas as pd
import os
from streamlit_extras.st_autorefresh import st_autorefresh

# Настройки страницы
st.set_page_config(page_title="Бункер — Панель игроков", layout="wide")
st.title("🎲 Бункер — Панель игроков")

# Пути к файлам
DATA_FILE = "players.csv"
CATASTROPHE_FILE = "catastrophe.txt"
BUNKER_FILE = "bunker.txt"

# Колонки таблицы
columns = [
    "Имя", "Профессия", "Пол / Возраст",
    "Здоровье", "Хобби", "Багаж", "Фобия", "Факт"
]

# Функции загрузки/сохранения данных
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_text(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_text(file_path, text):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

# Выбор роли
role = st.sidebar.selectbox("Выберите роль", ["Игрок", "Ведущий"])

if role == "Ведущий":
    password = st.sidebar.text_input("Введите пароль", type="password", placeholder="Введите пароль ведущего")
    if password != "admin123":
        st.warning("Неверный пароль. Попробуйте снова.")
        st.stop()
    else:
        st.sidebar.success("Вы вошли как Ведущий.")
else:
    st.sidebar.info("Вы просматриваете как Игрок (только просмотр).")

# Темная тема
st.markdown("""
    <style>
        body { background-color: #0e1117; color: #fafafa; }
        .stApp { background-color: #0e1117; }
        .stTextInput>div>div>input,
        .stNumberInput>div>input,
        .stTextArea textarea {
            background-color: #1e1e1e;
            color: white;
        }
        .stDataFrame, .stDataEditor {
            background-color: #1e1e1e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Инициализация состояния
if "players_df" not in st.session_state:
    st.session_state.players_df = load_data()

if "catastrophe_text" not in st.session_state:
    st.session_state.catastrophe_text = load_text(CATASTROPHE_FILE)

if "bunker_text" not in st.session_state:
    st.session_state.bunker_text = load_text(BUNKER_FILE)

# ========== БЛОК ДЛЯ ВЕДУЩЕГО ==========
if role == "Ведущий":
    st.subheader("🌍 Катастрофа")
    new_catastrophe = st.text_area("Опиши катастрофу", st.session_state.catastrophe_text, height=100)
    if new_catastrophe != st.session_state.catastrophe_text:
        st.session_state.catastrophe_text = new_catastrophe
        save_text(CATASTROPHE_FILE, new_catastrophe)

    st.subheader("🏚️ Бункер")
    new_bunker = st.text_area("Опиши бункер", st.session_state.bunker_text, height=100)
    if new_bunker != st.session_state.bunker_text:
        st.session_state.bunker_text = new_bunker
        save_text(BUNKER_FILE, new_bunker)

    with st.expander("➕ Добавить нового игрока"):
        with st.form("add_player_form"):
            name_input = st.text_input("Введите имя игрока")
            submitted = st.form_submit_button("Добавить игрока")
            if submitted:
                name = name_input.strip()
                if not name:
                    st.warning("Имя не может быть пустым.")
                elif name in st.session_state.players_df["Имя"].values:
                    st.warning("Игрок с таким именем уже существует.")
                else:
                    new_row = pd.DataFrame([[name] + [""] * (len(columns) - 1)], columns=columns)
                    st.session_state.players_df = pd.concat([st.session_state.players_df, new_row], ignore_index=True)
                    save_data(st.session_state.players_df)
                    st.success(f"Игрок {name} добавлен!")

    st.subheader("📋 Таблица игроков")
    st.info("Редактируйте характеристики игроков прямо в таблице:")

    edited_df = st.data_editor(
        st.session_state.players_df,
        num_rows="fixed",
        use_container_width=True
    )
    if not edited_df.equals(st.session_state.players_df):
        st.session_state.players_df = edited_df
        save_data(st.session_state.players_df)

    st.write("---")
    st.subheader("🗑️ Удаление игроков")
    to_delete = []
    for idx, name in enumerate(st.session_state.players_df["Имя"]):
        checked = st.checkbox(f"{name}", key=f"del_{idx}")
        if checked:
            to_delete.append(idx)

    if st.button("Удалить выбранных игроков"):
        if to_delete:
            st.session_state.players_df = st.session_state.players_df.drop(to_delete).reset_index(drop=True)
            save_data(st.session_state.players_df)
            st.success(f"Удалено игроков: {len(to_delete)}")
            for idx in to_delete:
                del st.session_state[f"del_{idx}"]
        else:
            st.warning("Выберите хотя бы одного игрока для удаления.")

    if st.button("🗑️ Очистить таблицу полностью"):
        st.session_state.players_df = pd.DataFrame(columns=columns)
        save_data(st.session_state.players_df)
        st.success("Таблица очищена.")

# ========== БЛОК ДЛЯ ИГРОКА ==========
else:
    # Автообновление каждые 10 секунд, обновляет только часть страницы без полной перезагрузки
    st_autorefresh(interval=10000, key="data_refresh")

    st.subheader("🌍 Катастрофа")
    st.markdown(load_text(CATASTROPHE_FILE))

    st.subheader("🏚️ Бункер")
    st.markdown(load_text(BUNKER_FILE))

    st.subheader("📋 Таблица игроков")
    st.dataframe(load_data(), use_container_width=True)
