import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株価可視化アプリ')

# サイドバーの設定：日数と株価の指定範囲
st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数', 1, 50, 20)

# **〇〇** 太字に設定
# f｛変数名} 数字を代入コメントで表示
st.write(f"""
### 過去 **{days}日間** のGAFA株価            
""")


@st.cache
def get_data(days, tickers):                            # get_data 数字と会社情報（名称、企業名コード)
    df = pd.DataFrame()                                 # DataFrame の母体
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])               # 企業の情報取得で企業名コードの入力
        hist = tkr.history(period=f'{days}d')           # 何日分の取得をするのか？
        hist.index = hist.index.strftime('%d %B %Y')    # 日付形式の入れ替え
        hist = hist[['Close']]                          # Close：最終株価の取得
        hist.columns = [company] 
        hist = hist.T                                   # 縦・横の入れ替え
        hist.index.name = 'Name'
        df = pd.concat([df, hist])                      # 接続
    return df

try: 
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(                     # 株価表示用の範囲を指定する
        '範囲を指定してください。',
        0.0, 3500.0, (0.0, 3500.0)
    )

    tickers = {                                         # 企業名、企業名コードの格納
        'apple': 'AAPL',
        'facebook': 'META',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tickers)
    companies = st.multiselect(                         # 選択・検索ツール？    〇〇業界の指定ができれば面白そう!
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]                         # df内の指定したcompanyのデータのみ取得する
        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()                      # データの縦・横の入れ替え＆データ表示用で加工する。reset(初期条件の数字が読み込めない？)
        data = pd.melt(data, id_vars=['Date']).rename(   # DATA変換 date,appleの株価、faceの株価, ⇒　date, apple(facebook), apple(facebook)の株価にする。　３⇒２ 
            columns={'value': 'Stock Prices(USD)'}       # 名前の変換をしている
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)           # 指定：clip=true はみ出したものを消す
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )