import pandas as pd
import streamlit as st
import requests
import streamlit_authenticator as stauth

# --- Autenticazione ---
names = ['Mario Rossi']
usernames = ['mrossi']
passwords = ['abc123']

hashed_passwords = stauth.Hasher(passwords).generate()
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'my_app', 'abcdef', cookie_expiry_days=30)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.success(f'Benvenuto, {name}!')

    # Titolo dell'app
    st.title("Analisi Cash Flow Immobiliare USA")

    st.markdown("""
    Questa app calcola il cash flow netto, il ROI semplice e il ROI con equity per immobili negli Stati Uniti su un periodo di 15 anni.
    """)

    # Funzione per calcolare mutuo mensile con 30% acconto e 6.5% interesse
    @st.cache_data
    def calcola_mutuo_mensile(prezzo, rate_annuo=6.5, acconto_perc=30):
        prestito = prezzo * (1 - acconto_perc / 100)
        rate_mensile = rate_annuo / 100 / 12
        n_rate = 30 * 12
        if rate_mensile == 0:
            return prestito / n_rate
        rata = prestito * (rate_mensile * (1 + rate_mensile)**n_rate) / ((1 + rate_mensile)**n_rate - 1)
        return rata

    # Input
    prezzo = st.number_input("Prezzo della casa ($)", min_value=0)
    affitto_mensile = st.number_input("Affitto mensile iniziale ($)", min_value=0)
    tasse_annue = st.number_input("Tasse annue sulla proprietà ($)", min_value=0)
    assicurazione_annua = st.number_input("Assicurazione annua ($)", min_value=0)
    hoa_annuo = st.number_input("HOA annuo ($)", min_value=0)
    gestione_annua = st.number_input("Gestione immobile annua ($)", min_value=0)
    manutenzione_annua = st.number_input("Manutenzione stimata annua ($)", min_value=0)
    vacanza_percentuale = st.number_input("Vacanza/sfitto (%)", min_value=0.0, max_value=100.0, value=5.0)
    tasso_apprezzamento = st.number_input("Apprezzamento annuo medio (%)", min_value=0.0, value=3.0)
    aumento_affitto = st.number_input("Aumento medio affitto annuo (%)", min_value=0.0, value=2.0)
    aumento_spese = st.number_input("Aumento medio spese annuo (%)", min_value=0.0, value=2.0)

    # Calcoli
    mutuo_mensile = calcola_mutuo_mensile(prezzo)
    mutuo_annuo = mutuo_mensile * 12
    capitale_iniziale = prezzo * 0.3
    prestito = prezzo * 0.7

    st.info(f"Mutuo mensile stimato: ${mutuo_mensile:,.2f}")

    result = []
    valore_casa = prezzo
    affitto = affitto_mensile * 12 * (1 - vacanza_percentuale / 100)
    spese = tasse_annue + assicurazione_annua + hoa_annuo + gestione_annua + manutenzione_annua + mutuo_annuo
    equity = 0

    for anno in range(1, 16):
        cashflow = affitto - spese
        equity += prestito / (30 * 12) * 12  # quota capitale stimata
        valore_casa *= (1 + tasso_apprezzamento / 100)
        affitto *= (1 + aumento_affitto / 100)
        spese *= (1 + aumento_spese / 100)

        roi_semplice = (cashflow * anno) / capitale_iniziale * 100
        roi_equity = ((cashflow * anno + equity + (valore_casa - prezzo)) / capitale_iniziale) * 100

        result.append({
            "Anno": anno,
            "Cashflow annuo": cashflow,
            "ROI % (solo cashflow)": roi_semplice,
            "ROI % (cashflow + equity + apprezzamento)": roi_equity
        })

    st.subheader("Proiezione ROI su 15 anni")
    df = pd.DataFrame(result)
    st.dataframe(df.style.format({
        "Cashflow annuo": "${:,.0f}",
        "ROI % (solo cashflow)": "{:.2f}%",
        "ROI % (cashflow + equity + apprezzamento)": "{:.2f}%"
    }))

elif authentication_status is False:
    st.error('Username o password errati')
elif authentication_status is None:
    st.warning('Inserisci le credenziali')
