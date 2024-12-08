import pandas as pd
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import os

# Membuat daftar tanggal manual dari 1 hingga 21 Oktober 2024
dates = [
    datetime(2024, 10, 1, 10, 0),
    datetime(2024, 10, 1, 12, 30),
    datetime(2024, 10, 1, 9, 15),
    datetime(2024, 10, 4, 14, 45),
    datetime(2024, 10, 5, 8, 20),
    datetime(2024, 10, 6, 18, 0),
    datetime(2024, 10, 7, 11, 0),
    datetime(2024, 10, 8, 15, 30),
    datetime(2024, 10, 9, 10, 15),
    datetime(2024, 10, 10, 16, 0),
    datetime(2024, 10, 11, 14, 30),
    datetime(2024, 10, 12, 11, 45),
    datetime(2024, 10, 13, 9, 0),
    datetime(2024, 10, 14, 19, 15),
    datetime(2024, 10, 15, 8, 30),
    datetime(2024, 10, 16, 17, 0),
    datetime(2024, 10, 17, 13, 30),
    datetime(2024, 10, 18, 10, 0),
    datetime(2024, 10, 19, 20, 0),
    datetime(2024, 10, 20, 9, 45),
    datetime(2024, 10, 21, 15, 30),
]

# Daftar teks dummy yang lebih panjang
texts = [
    "Kenapaaaaaa cuaca hari ini enak bgt, ya? Kayaknya pas bgt buat ke taman, biar bisa nikmatin udara segar sambil curhat sama temen-temen. 😄",
    "Sayaaaaa lg belajar Python, wow, seru bgt! Kalo ada tips atau trik buat newbie kayak saya, pls share ya! Bantuin bgt! 🤔",
    "Cuaca sejukkk hari ini bikin pengen ngumpul sambil ngopi. Gimana kalo kita ketemuan dan cerita-cerita seru? Pasti asyik bgt! ☕️",
    "Tadi liat orang jogging, langsung terinspirasi! Bikin pengen jadi lebih aktif. Kamu jg suka olahraga, kan? 🏃‍♂️",
    "Hari ini saya baca buku pengembangan diri, wow, makin semangat! Adaaa buku lain yang wajib dibaca? Pengen belajar terus! 📚",
    "Malam ini rencananya mau makan pizzzaaaa! Pizza itu makanan favvv saya! Kamu jg suka pizza? Topping fav kamu apa? 🍕",
    "Baru pulang dari pasar, beli bahan fresh buat masak. Akhir pekan ini mau masak apa, ya? Udah ada resep seru buat dicoba! 🍳",
    "Hari iniii pas bgt buat piknik! Siapa mau ikuttt? Rasanya asyik kalo bisa ngumpul dan bersenang-senang di luar! 🧺",
    "Weekend kemarin seru abis! Saya habisin waktu bareng keluargaaa. Gimana weekend kamu? Pasti ada cerita seru juga! 🎉",
    "Kemarin nonton film yang gilaaa asik! Ada rekomendasi film lain yang seru? Pengen nonton yang bikin ngakak atau baper gitu. 🎬",
    "Rencananya mau coba resep baru buat sarapan. Kamu ada resep enak yg gampang? Bantuin dong, butuh ide-ide fresh! 🍽️",
    "Cuaca hangat ini bikin pengen jalan-jalan ke tempat baru! Adaaa tempat seru yg kamu tau? Saya suka explore hal baru! 🌞",
    "Tadi ketemu temen lama, nostalgiaaaaa! Kapan kita bisa ketemu lg? Kangen sama momen seru yg kita lewatin bareng! 🕰️",
    "Cek ini: https://example.com, tempat ini super cocok buat piknik! Udah pernah kesana? Pasti seru buat relax! 🧺",
    "Baca info lebih lanjut di https://books.com tentang pengembangan diri! Banyak hal seru yg bisa dipelajari! 📚",
    "Kemarin nonton film terbaru di https://movies.com, dan itu bener-bener seru! Plot twist-nya bikin saya shocked, pengen nonton lg! 🎬",
    "Sekarang lagi nyoba hidup lebih sehat dengan olahraga. Kamu olahraga apa, nih? Pengennya bugar kayak kamu! 💪",
    "Eh, kenapa kamu ga bales pesan saya? 😅 Penasaran deh kamu sibuk sama apa. Ayo, jangan lupa balas, ya! 😜",
    "Makan es krim pas cuaca panas itu enakkkkk! 🍦 Siapa mau ajak saya makan es krim? Saya suka semua rasa, hehe! 😄",
    "Kapan kita bisa kumpul lg? Udah kangen bgt sama kamu! 🥰 Rasanya lamaaaa bgt ga ketemu, yuk kita atur waktu! 🎉",
    "Kemarin nonton film yang bikin baperrr! 🎥 Siapa mau nonton bareng lg minggu depan? Yuk kita atur jadwalnya! 🎉",
    "Tadi liat meme lucuuuuu yang bikin ngakak gila! 😂 Ayo kita bagi lebih banyak meme biar ketawa bareng! 🤣",
]

# Pastikan jumlah teks sama dengan jumlah tanggal
texts = texts[:len(dates)]  # Memastikan jumlah teks sama dengan jumlah tanggal

# Membuat DataFrame
data = {
    'Date': dates,
    'Text': texts
}

df_dummy = pd.DataFrame(data)

# Sort date
df_dummy = df_dummy.sort_values(by='Date')

# Convert the 'Date' column to datetime and remove time
df_dummy['Date'] = pd.to_datetime(df_dummy['Date']).dt.date

# Grouping date while preserving order and concatenating texts with a separator
df_dummy = df_dummy.groupby('Date', as_index=False).agg({
    'Text': lambda x: '. '.join(x.sort_index())
})

# Create a 'Week' column to split into 7-day intervals
min_date = pd.to_datetime(df_dummy['Date'].min())
df_dummy['Week'] = (pd.to_datetime(df_dummy['Date']) - min_date).dt.days // 7

# Group by the 'Week' column
df_weekly = df_dummy.groupby('Week', as_index=False).agg({
    'Text': 'sum',
    'Date': 'min'  
})

df_weekly = df_weekly[['Date', 'Text']] 

# ===========Data Cleaning===============

# remove slang (bahasa gaul)
from indoNLP.preprocessing import replace_slang

df_weekly['Text'] = df_weekly['Text'].apply(replace_slang)

# remove emoji
import emoji

def remove_emoji(teks):
    return emoji.replace_emoji(teks, replace='')

df_weekly['Text'] = df_weekly['Text'].apply(remove_emoji)

# remove elongation
from indoNLP.preprocessing import replace_word_elongation

df_weekly['Text'] = df_weekly['Text'].apply(replace_word_elongation)

# remove url
from indoNLP.preprocessing import remove_url

df_weekly['Text'] = df_weekly['Text'].apply(remove_url)

#Stop Words and Punctuation
from indoNLP.preprocessing import remove_stopwords
import string

class CleaningData:
    def __init__(self, text):
        self.text = text
        
    def clean_text(self):
        # Menghapus tanda baca kecuali koma dan titik
        text_no_other_punctuation = self.text.translate(str.maketrans('', '', string.punctuation.replace(',', '').replace('.', '')))
        
        # Menghapus spasi ekstra
        cleaned_text = ' '.join(text_no_other_punctuation.split())
        
        return cleaned_text.lower()

# Clean the text in the DataFrame using apply with a lambda function
df_weekly['Text'] = df_weekly['Text'].apply(lambda x: CleaningData(x).clean_text())

# Load environment variables
load_dotenv()

# Database connection details
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# Create a list of dictionaries for the data to insert
data_to_insert = [
    {'Date': row['Date'], 'text': row['Text']} 
    for index, row in df_weekly.iterrows()
]

def insert_db(data, schema_name, table_name):
    """Insert data into the specified table in the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cur = conn.cursor()
        
        # Construct SQL INSERT statement with schema and table
        insert_query = f"""
        INSERT INTO "{schema_name}"."{table_name}" (Date, text)
        VALUES (%s, %s);
        """
        
        # Insert each item in data with field name mapping
        for item in data:
            try:
                cur.execute(insert_query, (
                    item['Date'],  # Access 'week' directly
                    item['text'],  # Access 'text' directly
                ))
            except Exception as e:
                print(f"Error inserting item {item}: {e}")
        
        # Commit changes
        conn.commit()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        print(f"Data inserted successfully into {schema_name}.{table_name}.")
        
    except Exception as e:
        print(f"Error connecting to the database or inserting data: {e}")

# Call the function with the corrected data format
insert_db(data_to_insert, 'jpku', 'summarize_ai_7days')