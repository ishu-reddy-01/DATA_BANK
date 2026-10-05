import streamlit as st
from datetime import datetime
import sqlite3
import hashlib

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Data Bank",
    page_icon="📱",
    layout="wide"
)


# ==================================================
# DATABASE
# ==================================================

DB_NAME = "databank.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            pin TEXT NOT NULL,
            mobile_data REAL DEFAULT 2.0,
            data_bank REAL DEFAULT 0.0
        )
    """)

    # Transaction history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT NOT NULL,
            action TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# SECURITY
# ==================================================

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


# ==================================================
# USER FUNCTIONS
# ==================================================

def user_exists(mobile):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE mobile = ?",
        (mobile,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user(name, mobile, pin):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users
        (name, mobile, pin, mobile_data, data_bank)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        mobile,
        hash_pin(pin),
        2.0,
        0.0
    ))

    conn.commit()
    conn.close()


def verify_user(mobile, pin):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, pin
        FROM users
        WHERE mobile = ?
    """, (mobile,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    name, saved_pin = result

    if saved_pin == hash_pin(pin):
        return name

    return False


# ==================================================
# LOAD USER DATA
# ==================================================

def load_user_data(mobile):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mobile_data, data_bank
        FROM users
        WHERE mobile = ?
    """, (mobile,))

    result = cursor.fetchone()

    conn.close()

    return result


# ==================================================
# UPDATE USER DATA
# ==================================================

def update_balances(mobile, mobile_data, data_bank):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET mobile_data = ?,
            data_bank = ?
        WHERE mobile = ?
    """, (
        mobile_data,
        data_bank,
        mobile
    ))

    conn.commit()
    conn.close()


# ==================================================
# ADD TRANSACTION
# ==================================================

def add_transaction(mobile, action, amount):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (mobile, action, amount, date)
        VALUES (?, ?, ?, ?)
    """, (
        mobile,
        action,
        amount,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ))

    conn.commit()
    conn.close()


# ==================================================
# GET HISTORY
# ==================================================

def get_history(mobile):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT action, amount, date
        FROM transactions
        WHERE mobile = ?
        ORDER BY transaction_id DESC
    """, (mobile,))

    result = cursor.fetchall()

    conn.close()

    return result


# Create database automatically
create_database()


# ==================================================
# SESSION STATE
# ==================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_mobile" not in st.session_state:
    st.session_state.user_mobile = ""

if "create_account" not in st.session_state:
    st.session_state.create_account = False


# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #93c5fd,
        #c4b5fd
    );
    color: #172554;
}

.stApp p,
.stApp label,
.stApp span {
    color: #172554;
}

h1, h2, h3, h4 {
    color: #1e1b4b !important;
}

.login-box {
    background: #eef2ff;
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
    margin-top: 70px;
}

.login-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    color: #312e81 !important;
}

.login-subtitle {
    text-align: center;
    color: #475569 !important;
    font-size: 17px;
    margin-bottom: 25px;
}

.dashboard-title {
    font-size: 40px;
    font-weight: 700;
    color: #1e1b4b !important;
}

.card {
    background: #eef2ff;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.12);
    text-align: center;
}

.card h2 {
    color: #312e81 !important;
    margin-bottom: 5px;
}

.card p {
    color: #475569 !important;
}

section[data-testid="stSidebar"] {
    background: #e0e7ff;
}

section[data-testid="stSidebar"] * {
    color: #1e1b4b !important;
}

.stTextInput input,
.stNumberInput input {
    background-color: #ffffff !important;
    color: #172554 !important;
    border: 2px solid #818cf8 !important;
    border-radius: 10px !important;
}

.stButton > button {
    background: #4f46e5 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600;
}

.stButton > button:hover {
    background: #3730a3 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# LOGIN PAGE
# ==================================================

if not st.session_state.logged_in:

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.markdown(
            '<div class="login-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="login-title">📱 Data Bank</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="login-subtitle">'
            'Save your unused data. Use it when you need it.'
            '</div>',
            unsafe_allow_html=True
        )

        # ==================================================
        # LOGIN
        # ==================================================

        if not st.session_state.create_account:

            st.subheader("🔐 Login")

            mobile = st.text_input(
                "📱 Mobile Number",
                placeholder="Enter registered mobile number"
            )

            pin = st.text_input(
                "🔑 PIN",
                type="password",
                placeholder="Enter your 4-digit PIN"
            )

            if st.button(
                "🚀 Login",
                use_container_width=True
            ):

                if not mobile.isdigit() or len(mobile) != 10:

                    st.error(
                        "Please enter a valid 10-digit mobile number."
                    )

                elif not pin.isdigit() or len(pin) != 4:

                    st.error(
                        "Please enter your 4-digit PIN."
                    )

                else:

                    result = verify_user(mobile, pin)

                    if result is None:

                        st.error(
                            "Mobile number is not registered."
                        )

                    elif result is False:

                        st.error(
                            "Incorrect PIN."
                        )

                    else:

                        # Store login information
                        st.session_state.logged_in = True
                        st.session_state.user_name = result
                        st.session_state.user_mobile = mobile

                        st.success("Login successful!")

                        st.rerun()

            st.write("")

            if st.button(
                "🆕 Create New Account",
                use_container_width=True
            ):

                st.session_state.create_account = True
                st.rerun()

        # ==================================================
        # CREATE ACCOUNT
        # ==================================================

        else:

            st.subheader("🆕 Create Account")

            name = st.text_input(
                "👤 Name",
                placeholder="Enter your name"
            )

            mobile = st.text_input(
                "📱 Mobile Number",
                placeholder="Enter 10-digit mobile number"
            )

            pin = st.text_input(
                "🔐 Create 4-Digit PIN",
                type="password",
                placeholder="Create your PIN"
            )

            confirm_pin = st.text_input(
                "🔐 Confirm PIN",
                type="password",
                placeholder="Enter PIN again"
            )

            if st.button(
                "✅ Create Account",
                use_container_width=True
            ):

                if name.strip() == "":

                    st.error("Please enter your name.")

                elif not mobile.isdigit() or len(mobile) != 10:

                    st.error(
                        "Please enter a valid 10-digit mobile number."
                    )

                elif not pin.isdigit() or len(pin) != 4:

                    st.error(
                        "PIN must contain exactly 4 digits."
                    )

                elif pin != confirm_pin:

                    st.error("PINs do not match.")

                elif user_exists(mobile):

                    st.error(
                        "This mobile number is already registered."
                    )

                else:

                    create_user(
                        name,
                        mobile,
                        pin
                    )

                    st.success(
                        "Account created successfully!"
                    )

                    st.session_state.create_account = False

                    st.rerun()

            st.write("")

            if st.button(
                "⬅️ Back to Login",
                use_container_width=True
            ):

                st.session_state.create_account = False
                st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.caption(
            "🔒 Your account data is stored securely in the database."
        )


# ==================================================
# MAIN APPLICATION
# ==================================================

else:

    # --------------------------------------------------
    # GET USER DATA FROM DATABASE
    # --------------------------------------------------

    user_data = load_user_data(
        st.session_state.user_mobile
    )

    if user_data is None:

        st.session_state.logged_in = False
        st.rerun()

    mobile_data, data_bank = user_data


    # ==================================================
    # SIDEBAR
    # ==================================================

    st.sidebar.title("📱 Data Bank")

    st.sidebar.success(
        f"Welcome, {st.session_state.user_name}!"
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "💾 Save Data",
            "🔄 Use Data",
            "📜 History",
            "🤖 Smart Prediction"
        ]
    )

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_mobile = ""

        st.rerun()


    # ==================================================
    # DASHBOARD
    # ==================================================

    if page == "🏠 Dashboard":

        st.markdown(
            '<div class="dashboard-title">'
            f'Hello, {st.session_state.user_name}! 👋'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Manage your unused mobile data with Data Bank."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                f"""
                <div class="card">
                    <h2>📶 {mobile_data:.2f} GB</h2>
                    <p>Current Mobile Data</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="card">
                    <h2>🏦 {data_bank:.2f} GB</h2>
                    <p>Data Bank Balance</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            total = mobile_data + data_bank

            st.markdown(
                f"""
                <div class="card">
                    <h2>📦 {total:.2f} GB</h2>
                    <p>Total Available</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        st.subheader("🏦 Data Bank Storage")

        progress = min(data_bank / 10, 1.0)

        st.progress(progress)

        st.write(
            f"{data_bank:.2f} GB / 10 GB"
        )


    # ==================================================
    # SAVE DATA
    # ==================================================

    elif page == "💾 Save Data":

        st.header("💾 Save Unused Data")

        st.write(
            f"Current balance: **{mobile_data:.2f} GB**"
        )

        if mobile_data > 0:

            amount = st.number_input(
                "Amount to save (GB)",
                min_value=0.1,
                max_value=float(mobile_data),
                step=0.1
            )

            if st.button("💾 Save Data"):

                if data_bank + amount > 10:

                    st.error(
                        "Data Bank maximum storage is 10 GB."
                    )

                else:

                    # Automatically calculate new balances
                    new_mobile_data = mobile_data - amount
                    new_data_bank = data_bank + amount

                    # Save balances to database
                    update_balances(
                        st.session_state.user_mobile,
                        new_mobile_data,
                        new_data_bank
                    )

                    # Save transaction
                    add_transaction(
                        st.session_state.user_mobile,
                        "Data Saved",
                        amount
                    )

                    st.success(
                        f"{amount:.2f} GB saved successfully!"
                    )

                    st.rerun()

        else:

            st.warning(
                "You don't have enough mobile data."
            )


    # ==================================================
    # USE DATA
    # ==================================================

    elif page == "🔄 Use Data":

        st.header("🔄 Use Data Bank")

        st.write(
            f"Data Bank balance: **{data_bank:.2f} GB**"
        )

        if data_bank > 0:

            amount = st.number_input(
                "Amount to use (GB)",
                min_value=0.1,
                max_value=float(data_bank),
                step=0.1
            )

            if st.button("🔄 Use Data"):

                # Automatically calculate new balances
                new_data_bank = data_bank - amount
                new_mobile_data = mobile_data + amount

                # Save balances
                update_balances(
                    st.session_state.user_mobile,
                    new_mobile_data,
                    new_data_bank
                )

                # Save transaction
                add_transaction(
                    st.session_state.user_mobile,
                    "Data Used",
                    amount
                )

                st.success(
                    f"{amount:.2f} GB restored to your balance!"
                )

                st.rerun()

        else:

            st.warning(
                "Your Data Bank is empty."
            )


    # ==================================================
    # HISTORY
    # ==================================================

    elif page == "📜 History":

        st.header("📜 Transaction History")

        history = get_history(
            st.session_state.user_mobile
        )

        if not history:

            st.info("No transactions yet.")

        else:

            for action, amount, date in history:

                st.write(
                    f"**{action}** | "
                    f"{amount:.2f} GB | "
                    f"{date}"
                )


    # ==================================================
    # SMART PREDICTION
    # ==================================================

    elif page == "🤖 Smart Prediction":

        st.header("🤖 Smart Data Prediction")

        st.write(
            "Predict how much data may remain unused today."
        )

        daily_plan = st.number_input(
            "Daily data plan (GB)",
            min_value=0.5,
            value=2.0,
            step=0.5
        )

        expected_usage = st.number_input(
            "Expected usage (GB)",
            min_value=0.0,
            max_value=daily_plan,
            value=1.2,
            step=0.1
        )

        predicted_unused = (
            daily_plan - expected_usage
        )

        if predicted_unused > 0:

            st.success(
                f"🤖 Estimated unused data: "
                f"**{predicted_unused:.2f} GB**"
            )

            st.info(
                "You could save this amount in your Data Bank."
            )

        else:

            st.info(
                "You are expected to use most of today's data."
            )