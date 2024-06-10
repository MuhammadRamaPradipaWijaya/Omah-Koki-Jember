import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
import jwt
from datetime import datetime
import requests

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
        harga = float(request.form.get('harga'))
        deskripsi = request.form.get('deskripsi')
        kondisi = request.form.get('kondisi')
        berat = float(request.form.get('berat'))
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
        harga = float(request.form.get('harga'))
        deskripsi = request.form.get('deskripsi')
        kondisi = request.form.get('kondisi')
        berat = float(request.form.get('berat'))
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
    pembayaran = list(db.pembayaran.find({}))
    return render_template('ad_pembayaran.html', pembayaran = pembayaran)

@app.route('/addpembayaran', methods=['GET','POST'])
def addpembayaran():
    if request.method == 'POST':
        bank = request.form.get('bank')
        pemilik = request.form.get('pemilikrek')
        norek = request.form.get('norek')

        doc = {
            'Nama_Bank' : bank,
            'Pemilik_Rek' : pemilik,
            'No_Rek' : norek 
        }
        db.pembayaran.insert_one(doc)
        return redirect(url_for('adpembayaran'))
    return render_template('ad_pembayaran.html')

@app.route('/editPembayaran/<_id>', methods=['GET', 'POST'])
def editPembayaran(_id):
    if request.method == 'POST':
        bank = request.form.get('bank')
        pemilik = request.form.get('pemilikrek')
        norek = request.form.get('norek')

        doc = {
            'Nama_Bank' : bank,
            'Pemilik_Rek' : pemilik,
            'No_Rek' : norek 
        }
        db.pembayaran.update_one({'_id': ObjectId(_id)}, {'$set': doc})
        return redirect(url_for('adpembayaran'))
    id = ObjectId(_id)
    pembayaran =list(db.pembayaran.find({'_id': id}))
    return render_template('ad_pembayaran.html', pembayaran=pembayaran)

@app.route('/deletePembayaran/<_id>',methods=['GET','POST'])
def deletePembayaran(_id):
    db.pembayaran.delete_one({'_id': ObjectId(_id)})
    return redirect(url_for('adpembayaran'))

@app.route('/adpengiriman')
def adpengiriman():
    pengiriman = list(db.pengiriman.find({}))
    return render_template('ad_pengiriman.html', pengiriman=pengiriman)

@app.route('/tambah_pengiriman', methods=['POST'])
def tambah_pengiriman():
    if request.method == 'POST':
        jasa_kirim = request.form.get('jasa_kirim')
        tarif_dalam_kota = request.form.get('tarif_dalam_kota')
        estimasi_dalam_kota = request.form.get('estimasi_dalam_kota')
        tarif_luar_kota = request.form.get('tarif_luar_kota')
        estimasi_luar_kota = request.form.get('estimasi_luar_kota')
        tarif_luar_provinsi = request.form.get('tarif_luar_provinsi')
        estimasi_luar_provinsi = request.form.get('estimasi_luar_provinsi')
        tarif_luar_pulau = request.form.get('tarif_luar_pulau')
        estimasi_luar_pulau = request.form.get('estimasi_luar_pulau')
        
        db.pengiriman.insert_one({
            'jasa_kirim': jasa_kirim,
            'zona': {
                'dalam kota':{
                    'tarif': tarif_dalam_kota,
                    'estimasi': estimasi_dalam_kota
                },
                'luar kota':{
                    'tarif': tarif_luar_kota,
                    'estimasi': estimasi_luar_kota
                },
                'luar provinsi':{
                    'tarif': tarif_luar_provinsi,
                    'estimasi': estimasi_luar_provinsi
                },
                'luar pulau':{
                    'tarif': tarif_luar_pulau,
                    'estimasi': estimasi_luar_pulau
                }
            }
        })
        return redirect(url_for('adpengiriman'))
    return render_template('ad_pengiriman.html')

@app.route('/tambah_kota', methods=['POST'])
def tambah_kota():
    if request.method == 'POST':
        jasa_kirim = request.form.get('jasa_kirim')
        zona_tarif = request.form.get('zona_tarif')
        nama_kota = request.form.get('nama_kota')
        
        db.pengiriman.update_one(
            {'jasa_kirim': jasa_kirim},
            {
                '$push': {
                    'zona.' + zona_tarif.lower() + '.kota-kabupaten': nama_kota
                }
            }
        )
        return redirect(url_for('adpengiriman'))

@app.route('/editpengiriman/<pengiriman_id>', methods=['GET', 'POST'])
def editpengiriman(pengiriman_id):
    if request.method == 'POST':
        jasa_kirim = request.form.get('jasa_kirim')
        tarif_dalam_kota = request.form.get('tarif_dalam_kota')
        estimasi_dalam_kota = request.form.get('estimasi_dalam_kota')
        tarif_luar_kota = request.form.get('tarif_luar_kota')
        estimasi_luar_kota = request.form.get('estimasi_luar_kota')
        tarif_luar_provinsi = request.form.get('tarif_luar_provinsi')
        estimasi_luar_provinsi = request.form.get('estimasi_luar_provinsi')
        tarif_luar_pulau = request.form.get('tarif_luar_pulau')
        estimasi_luar_pulau = request.form.get('estimasi_luar_pulau')

        db.pengiriman.update_one({'_id': ObjectId(pengiriman_id)}, {
            '$set': {
                'jasa_kirim': jasa_kirim,
                'zona.dalam kota.tarif': tarif_dalam_kota,
                'zona.dalam kota.estimasi': estimasi_dalam_kota,
                'zona.luar kota.tarif': tarif_luar_kota,
                'zona.luar kota.estimasi': estimasi_luar_kota,
                'zona.luar provinsi.tarif': tarif_luar_provinsi,
                'zona.luar provinsi.estimasi': estimasi_luar_provinsi,
                'zona.luar pulau.tarif': tarif_luar_pulau,
                'zona.luar pulau.estimasi': estimasi_luar_pulau
            }
        })
        return redirect(url_for('adpengiriman'))
    return render_template('ad_pengiriman.html')

@app.route('/hapus_pengiriman/<pengiriman_id>', methods=['POST'])
def hapus_pengiriman(pengiriman_id):
    db.pengiriman.delete_one({'_id': ObjectId(pengiriman_id)})
    return redirect(url_for('adpengiriman'))

@app.route('/edit_kota/<nama_kota>', methods=['POST'])
def edit_kota(nama_kota):
    if request.method == 'POST':
        nama_baru = request.form['nama_baru']
        for item in db.pengiriman.find({}):
            for zona, detail_zona in item['zona'].items():
                if nama_kota in detail_zona.get('kota-kabupaten', []):
                    db.pengiriman.update_one(
                        {'_id': item['_id'], 'zona.' + zona + '.kota-kabupaten': nama_kota},
                        {'$set': {'zona.' + zona + '.kota-kabupaten.$': nama_baru}}
                    )
        return redirect(url_for('adpengiriman'))

@app.route('/hapus_kota/<nama_kota>', methods=['POST'])
def hapus_kota(nama_kota):
    if request.method == 'POST':
        for item in db.pengiriman.find({}):
            for zona, detail_zona in item['zona'].items():
                if nama_kota in detail_zona.get('kota-kabupaten', []):
                    db.pengiriman.update_one(
                        {'_id': item['_id']},
                        {'$pull': {'zona.' + zona + '.kota-kabupaten': nama_kota}}
                    )
        return redirect(url_for('adpengiriman'))

@app.route('/adpengguna')
def adpengguna():
    users = list(db.pembeli.find())
    return render_template('ad_pengguna.html', users=users)

@app.route('/toggle-blokir/<id>', methods=['POST'])
def blokir(id):
    diblokir = False
    user = db.pembeli.find_one({'_id': ObjectId(id)})


    if "diblokir" in user :
        if user['diblokir'] == True :
            diblokir = False
        else:
            diblokir = True

    db.pembeli.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'diblokir': diblokir}}
    )
    return redirect(url_for('adpengguna'))

@app.route('/adprofil', methods=['GET', 'POST'])
def adprofil():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST' :
            admin = db.admin.find_one({'_id': ObjectId(session['user_id'])})

            nama = request.form['username']
            gender = request.form['gender']
            tgl_lahir = request.form['tgl_lahir']
            telepon = request.form['telepon']

            today = datetime.now()
            mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
            
            admin_img = request.files.get('profil')
            filename = admin.get('avatar', '')

            if (admin_img) :
                extension = admin_img.filename.split('.')[-1]
                filename = f'admin-{mytime}.{extension}'
                save_to = os.path.join('static/ad_assets/profil_admin', filename)        
                admin_img.save(save_to)

            data = {
                'nama' : nama,
                'telepon' : telepon,
                'gender' : gender,
                'tgl_lahir' : tgl_lahir,
                'avatar' : filename
            }

            if request.form['password']:
                data['password'] = jwt.encode({'password': request.form['password']}, SECRET_KEY, algorithm='HS256')

            db.admin.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$set': data}
            )
            

            session['username'] = nama
            session['telepon'] = telepon
            session['tgl_lahir'] = tgl_lahir
            session['gender'] = gender
            session['avatar'] = filename

            return redirect(url_for('adprofil'))
        else :
            return render_template('ad_profil.html')
    else:
        return redirect(url_for('adlogin'))
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
        user_id = session['user_id']
        produk_id = request.form.get('produk_id')
        jumlah = int(request.form.get('jumlah'))

        produk = db.adproduk.find_one({'_id': ObjectId(produk_id)})

        if produk:
            existing_item = db.keranjang.find_one({'user_id': user_id, 'produk_id': produk_id})

            if existing_item:
                total_jumlah = existing_item['jumlah'] + jumlah
                total_berat = total_jumlah * produk['berat']
                db.keranjang.update_one({'_id': existing_item['_id']}, {'$set': {'jumlah': total_jumlah, 'berat': total_berat}})
                return redirect(url_for('keranjang'))
            else:
                item_keranjang = {
                    'user_id': user_id,
                    'produk_id': produk_id,
                    'jumlah': jumlah,
                    'nama_produk': produk['nama_produk'],
                    'harga': produk['harga'],
                    'berat': (jumlah * produk['berat']),
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
        user_id = session['user_id']
        items_keranjang = list(db.keranjang.find({'user_id': user_id}))
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

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        items_keranjang = list(db.keranjang.find({'user_id': user_id}))
        subtotal = sum(int(item['harga']) * int(item['jumlah']) for item in items_keranjang)
        pengiriman_list = list(db.pengiriman.find({}))
        pembayaran_list = list(db.pembayaran.find({}))
        return render_template('checkout.html', items_keranjang=items_keranjang, subtotal=subtotal, pengiriman_list=pengiriman_list, pembayaran_list=pembayaran_list)
    else:
        return redirect(url_for('login'))

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            pembeli = db.pembeli.find_one({'_id': ObjectId(session['user_id'])})

            nama = request.form['nama']
            tglLahir = request.form['tglLahir']
            gender = request.form['gender']
            telepon = request.form['telepon']

            today = datetime.now()
            mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

            pembeli_img = request.files['image']
            filename = pembeli.get('image', '')
            if pembeli_img:
                extension = pembeli_img.filename.split('.')[-1]
                filename = f'pembeli-{mytime}.{extension}'
                save_to = os.path.join('static/assets/profil_pembeli', filename)
                pembeli_img.save(save_to)
            
            doc = {
                'nama': nama,
                'tglLahir': tglLahir,
                'gender': gender,
                'telepon': telepon,
                'image': filename
            }

            if request.form['password']:
                doc['password'] = jwt.encode({'password': request.form['password']}, SECRET_KEY, algorithm='HS256')

            db.pembeli.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$set': doc}
            )

            session['nama'] = nama
            session['tglLahir'] = tglLahir
            session['gender'] = gender
            session['telepon'] = telepon
            session['image'] = filename

            return redirect(url_for('profil'))
        else:
            pembeli = db.pembeli.find_one({'_id': ObjectId(session['user_id'])})
            return render_template('profil.html', pembeli=pembeli)
    else:
        return redirect(url_for('login'))
# BAGIAN USER #


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.pembeli.find_one({'email': email})

        if 'diblokir' in user and user['diblokir'] == True :
            return render_template('login.html', error="Akun ini terblokir")
        
        if user and jwt.decode(user['password'], SECRET_KEY, algorithms=['HS256'])['password'] == password:
            session['logged_in'] = True
            session['username'] = user['nama']
            session['user_id'] = str(user['_id'])
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
        
        user_id = db.pembeli.insert_one({
            'nama': nama,
            'telepon': telepon,
            'email': email,
            'password': token,
            'tgl_registrasi': tanggal_registrasi
        }).inserted_id
        
        session['logged_in'] = True
        session['username'] = nama
        session['user_id'] = str(user_id)
        
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
            session['email'] = user['email']
            session['telepon'] = user['telepon']
            session['tgl_registrasi'] = user['tgl_registrasi']
            if 'avatar' in user:
                session['avatar'] = user['avatar']
            session['user_id'] = str(user['_id'])
            
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
        user_id = db.admin.insert_one({
            'nama': nama,
            'telepon': telepon,
            'email': email,
            'password': token,
            'tgl_registrasi': tanggal_registrasi
        }).inserted_id
        
        session['logged_in'] = True
        session['username'] = nama
        session['email'] = email
        session['telepon'] = telepon
        session['tgl_registrasi'] = tanggal_registrasi
        session['user_id'] = str(user_id)
        
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
    session.pop('username', None)
    session.pop('email', None)
    session.pop('telepon', None)
    session.pop('tgl_registrasi', None)
    session.pop('avatar', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)