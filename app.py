from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# BAGIAN ADMIN #
@app.route('/dashboard')
def dashboard():
    return render_template('ad_index.html')

@app.route('/adpesanan')
def adpesanan():
    return render_template('ad_pesanan.html')

@app.route('/adproduk')
def adproduk():
    return render_template('ad_produk.html')

@app.route('/adpelanggan')
def adpelanggan():
    return render_template('ad_pelanggan.html')

@app.route('/adlpenjualan')
def adlpenjualan():
    return render_template('ad_lpenjualan.html')

@app.route('/adlproduk')
def adlproduk():
    return render_template('ad_lproduk.html')

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
# BAGIAN USER #



if __name__ == '__main__':
    app.run(port=5000,debug=True)