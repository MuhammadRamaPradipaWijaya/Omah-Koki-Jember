import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
import jwt
from datetime import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

SECRET_KEY = 'OKJ'
app.secret_key = SECRET_KEY

# BAGIAN ADMIN #
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        return render_template('ad_index.html')
    else:
        return redirect(url_for('adlogin'))

@app.route('/adpesanan', methods=['GET', 'POST'])
def adpesanan():
    return render_template('ad_pesanan.html')

@app.route('/order/confirmation')
def order_confirmation():
    name = request.args.get('name')
    item = request.args.get('item')
    return f'Terima kasih, {name}! Pesanan Anda untuk {item} telah diterima.'

@app.route('/adproduk', methods=['GET', 'POST'])
def adproduk():
    produk = list(db.adproduk.find({}))
    return render_template('ad_produk.html', produk=produk)

@app.route('/addProduk', methods=['GET', 'POST'])
def addProduk():
    if request.method == 'POST':
        produk = request.form.get('namaProduk')
        stock = request.form.get('stock')
        harga = request.form.get('harga')
        deskripsi = request.form.get('deskripsi')
        kondisi = request.form.get('kondisi')
        berat = request.form.get('berat')
        kategori = request.form.get('kategori')
        panjang = request.form.get('panjang')
        lebar = request.form.get('lebar')
        tinggi = request.form.get('tinggi')

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

        produk_file = request.files.get('gambar')
        extension = produk_file.filename.split('.')[-1]
        filename = f'produk-{mytime}.{extension}'
        save_to = os.path.join('static/ad_assets/imgproduk', filename)        
        produk_file.save(save_to)
        
        doc = {
            'nama_produk' : produk,
            'stock' : stock,
            'harga' : harga,
            'gambar' : filename,
            'deskripsi' : deskripsi,
            'kondisi' : kondisi,
            'berat' : berat,
            'kategori' : kategori,
            'panjang' : panjang,
            'lebar' : lebar,
            'tinggi' : tinggi
        }
        db.adproduk.insert_one(doc)
        return redirect(url_for('adproduk'))
    return render_template('ad_produk.html')

@app.route('/editProduk/<_id>', methods=['GET', 'POST'])
def editProduk(_id):
    if request.method == 'POST':
        produk = request.form.get('namaProduk')
        stock = request.form.get('stock')
        harga = request.form.get('harga')
        deskripsi = request.form.get('deskripsi')
        kondisi = request.form.get('kondisi')
        berat = request.form.get('berat')
        kategori = request.form.get('kategori')
        panjang = request.form.get('panjang')
        lebar = request.form.get('lebar')
        tinggi = request.form.get('tinggi')

        produk_sebelumnya = db.adproduk.find_one({'_id': ObjectId(_id)})
        if not produk_sebelumnya:
            return redirect(url_for('adproduk'))

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

        produk_file = request.files.get('gambar')
        if produk_file and produk_file.filename != '':
            extension = produk_file.filename.split('.')[-1]
            filename = f'produk-{mytime}.{extension}'
            save_to = os.path.join('static/ad_assets/imgproduk', filename)
            produk_file.save(save_to)
        else:
            filename = produk_sebelumnya.get('gambar')

        doc = {
            'nama_produk' : produk,
            'stock' : stock,
            'harga' : harga,
            'gambar' : filename,
            'deskripsi' : deskripsi,
            'kondisi' : kondisi,
            'berat' : berat,
            'kategori' : kategori,
            'panjang' : panjang,
            'lebar' : lebar,
            'tinggi' : tinggi
        }
            
        db.adproduk.update_one({'_id': ObjectId(_id)}, {'$set': doc})
        return redirect(url_for('adproduk'))
    else:
        produk = db.adproduk.find_one({'_id': ObjectId(_id)})
        if produk:
            return render_template('ad_produk.html', produk=produk)

@app.route('/deleteProduk/<_id>',methods=['GET','POST'])
def deleteProduk(_id):
    db.adproduk.delete_one({'_id': ObjectId(_id)})
    return redirect(url_for('adproduk'))

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
    produk_terbaru = list(db.adproduk.find().sort('_id', -1).limit(3))
    return render_template('index.html', produk_terbaru=produk_terbaru)

@app.route('/produk', methods=['GET'])
def produk():
    filter_kategori = request.args.get('kategori')
    page = int(request.args.get('page', 1))
    per_page = 9

    if filter_kategori:
        produk_count = db.adproduk.count_documents({"kategori": filter_kategori})
        produk_list = list(db.adproduk.find({"kategori": filter_kategori}).skip((page - 1) * per_page).limit(per_page))
    else:
        produk_count = db.adproduk.count_documents({})
        produk_list = list(db.adproduk.find({}).skip((page - 1) * per_page).limit(per_page))

    total_pages = (produk_count + per_page - 1) // per_page
    return render_template('produk.html', produk=produk_list, total_pages=total_pages, current_page=page, filter_kategori=filter_kategori)

@app.route('/detailproduk/<produk_id>', methods=['GET'])
def detail_produk(produk_id):
    produk = db.adproduk.find_one({'_id': ObjectId(produk_id)})
    return render_template('detail_produk.html', produk=produk)

@app.route('/tambah_ke_keranjang', methods=['POST'])
def tambah_ke_keranjang():
    if 'logged_in' in session and session['logged_in']:
        email_pengguna = session['username']
        produk_id = request.form.get('produk_id')
        jumlah = request.form.get('jumlah')

        produk = db.adproduk.find_one({'_id': ObjectId(produk_id)})

        if produk:
            existing_item = db.keranjang.find_one({'email_pengguna': email_pengguna, 'produk_id': produk_id})

            if existing_item:
                db.keranjang.update_one({'_id': existing_item['_id']}, {'$set': {'jumlah': jumlah}})
                return redirect(url_for('keranjang'))
            else:
                item_keranjang = {
                    'email_pengguna': email_pengguna,
                    'produk_id': produk_id,
                    'jumlah': jumlah,
                    'nama_produk': produk['nama_produk'],
                    'harga': produk['harga'],
                    'gambar': produk['gambar']
                }
                db.keranjang.insert_one(item_keranjang)
                return redirect(url_for('keranjang'))
        else:
            return jsonify({'status': 'gagal', 'pesan': 'Produk tidak ditemukan'})
    else:
        return redirect(url_for('login'))


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
    if 'logged_in' in session and session['logged_in']:
        email_pengguna = session['username']
        items_keranjang = list(db.keranjang.find({'email_pengguna': email_pengguna}))
        subtotal = sum(int(item['harga']) * int(item['jumlah']) for item in items_keranjang)
        return render_template('keranjang.html', items_keranjang=items_keranjang, subtotal=subtotal)
    else:
        return redirect(url_for('login'))
    
@app.route('/hapus_dari_keranjang/<item_id>', methods=['POST'])
def hapus_dari_keranjang(item_id):
    if 'logged_in' in session and session['logged_in']:
        db.keranjang.delete_one({'_id': ObjectId(item_id)})
        return redirect(url_for('keranjang'))
    else:
        return redirect(url_for('login'))

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/profil')
def profil():
    return render_template('profil.html')
# BAGIAN USER #


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.pembeli.find_one({'email': email})
        if user and jwt.decode(user['password'], SECRET_KEY, algorithms=['HS256'])['password'] == password:
            session['logged_in'] = True
            session['username'] = user['nama']
            return redirect(url_for('home'))
        else:
            error = 'Email atau kata sandi salah. Silakan coba lagi.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        telepon = request.form['telepon']
        email = request.form['email']
        password = request.form['password']
        
        token = jwt.encode({'password': password}, SECRET_KEY, algorithm='HS256')
        
        tanggal_registrasi = datetime.utcnow().strftime('%Y-%m-%d')
        
        db.pembeli.insert_one({
            'nama': nama,
            'telepon': telepon,
            'email': email,
            'password': token,
            'tgl_registrasi': tanggal_registrasi
        })
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/cek_email_pembeli', methods=['POST'])
def cek_email_pembeli():
    email = request.form['email']
    existing_user = db.pembeli.find_one({'email': email})
    if existing_user:
        return jsonify({'status': 'fail'})
    else:
        return jsonify({'status': 'success'})

@app.route('/adlogin', methods=['GET', 'POST'])
def adlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.admin.find_one({'email': email})
        if user and jwt.decode(user['password'], SECRET_KEY, algorithms=['HS256'])['password'] == password:
            session['logged_in'] = True
            session['username'] = user['nama']
            return redirect(url_for('dashboard'))
        else:
            error = 'Email atau kata sandi salah. Silakan coba lagi.'
            return render_template('ad_login.html', error=error)
    return render_template('ad_login.html')

@app.route('/adregister', methods=['GET', 'POST'])
def adregister():
    if request.method == 'POST':
        nama = request.form['nama']
        telepon = request.form['telepon']
        email = request.form['email']
        password = request.form['password']
        
        token = jwt.encode({'password': password}, SECRET_KEY, algorithm='HS256')
        
        tanggal_registrasi = datetime.utcnow().strftime('%Y-%m-%d')
        db.admin.insert_one({
            'nama': nama,
            'telepon': telepon,
            'email': email,
            'password': token,
            'tgl_registrasi': tanggal_registrasi
        })
        
        return redirect(url_for('adlogin'))
    return render_template('ad_register.html')

@app.route('/cek_email_admin', methods=['POST'])
def cek_email():
    email = request.form['email']
    existing_user = db.admin.find_one({'email': email})
    if existing_user:
        return jsonify({'status': 'fail'})
    else:
        return jsonify({'status': 'success'})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)