import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Бункер — Панель игроков", layout="wide")
st.title("🎲 Бункер — Панель игроков")

# 📁 Файл, в который сохраняются игроки
DATA_FILE = "players.csv"

# 📄 Структура таблицы
columns = [
    "Имя", "Профессия", "Пол / Возраст",
    "Здоровье", "Хобби", "Багаж", "Фобия", "Факт"
]

# 📥 Загрузка данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=columns)

# 💾 Сохранение данных в файл
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 🔑 Роль пользователя
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

# 🎨 Темная тема
st.markdown("""
    <style>
        body { background-color: #0e1117; color: #fafafa; }
        .stApp { background-color: #0e1117; }
        .stTextInput>div>div>input,
        .stNumberInput>div>input {
            background-color: #1e1e1e;
            color: white;
        }
        .stDataFrame, .stDataEditor {
            background-color: #1e1e1e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 📦 Загружаем или инициализируем данные
if "players_df" not in st.session_state:
    st.session_state.players_df = load_data()

# ➕ Добавление нового игрока
if role == "Ведущий":
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

# 📋 Таблица игроков
st.subheader("📋 Таблица игроков")

if role == "Ведущий":
    st.info("Редактируйте характеристики игроков прямо в таблице:")

    # 📝 Редактируемая таблица
    edited_df = st.data_editor(
        st.session_state.players_df,
        num_rows="fixed",
        use_container_width=True
    )
    if not edited_df.equals(st.session_state.players_df):
        st.session_state.players_df = edited_df
        save_data(st.session_state.players_df)

    st.write("---")

    # ❌ Удаление игроков
    st.subheader("🗑️ Выберите игроков для удаления")
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

    # 🧹 Очистка всей таблицы
    if st.button("🗑️ Очистить таблицу полностью"):
        st.session_state.players_df = pd.DataFrame(columns=columns)
        save_data(st.session_state.players_df)
        st.success("Таблица очищена.")

else:
    # 👀 Только просмотр для игроков
    st.dataframe(st.session_state.players_df, use_container_width=True)
