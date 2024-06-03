import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

# BAGIAN ADMIN #
@app.route('/dashboard')
def dashboard():
    return render_template('ad_index.html')

@app.route('/adpesanan', methods=['GET', 'POST'])
def adpesanan():
    return render_template('ad_pesanan.html')

@app.route('/order/confirmation')
def order_confirmation():
    name = request.args.get('name')
    item = request.args.get('item')
    return f'Terima kasih, {name}! Pesanan Anda untuk {item} telah diterima.'

@app.route('/adproduk')
def adproduk():
    return render_template('ad_produk.html')

@app.route('/adpelanggan')
def adpelanggan():
    return render_template('ad_pelanggan.html')

@app.route('/adlpenjualan')
def adlpenjualan():
    return render_template('ad_lpenjualan.html')

@app.route('/adlpenjualan/cetak')
def cetakLaporanPenjualan():
    return render_template('cetak_laporan_penjualan.html')

@app.route('/adlproduk')
def adlproduk():
    return render_template('ad_lproduk.html')

@app.route('/adlproduk/cetak')
def cetakLaporanProduk():
    return render_template('cetak_laporan_produk.html')

@app.route('/adpembayaran')
def adpembayaran():
    return render_template('ad_pembayaran.html')

@app.route('/adpengiriman')
def adlpengiriman():
    return render_template('ad_pengiriman.html')

@app.route('/adpengguna')
def adlpengguna():
    return render_template('ad_pengguna.html')

@app.route('/adprofil')
def adprofil():
    return render_template('ad_profil.html')
# BAGIAN ADMIN #



# BAGIAN USER #
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/produk')
def produk():
    return render_template('produk.html')

@app.route('/detailproduk')
def detailproduk():
    return render_template('detail_produk.html')

@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

@app.route('/pesanan')
def pesanan():
    return render_template('pesanan.html')

@app.route('/keranjang')
def keranjang():
    return render_template('keranjang.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/profil')
def profil():
    return render_template('profil.html')
# BAGIAN USER #


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/adlogin')
def adlogin():
    return render_template('ad_login.html')

@app.route('/adregister')
def adregister():
    return render_template('ad_register.html')


if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)