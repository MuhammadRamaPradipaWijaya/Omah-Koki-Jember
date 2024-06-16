import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
import jwt
from datetime import datetime, timedelta
import hashlib

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
        pesanan = list(db.pesanan.find({'status': 'selesai'}))
        jumlah_produk = db.adproduk.count_documents({})
        jumlah_pengguna = db.pembeli.count_documents({})
        jumlah_pesanan_selesai = db.pesanan.count_documents({'status': 'selesai'})
        return render_template('ad_index.html', pesanan=pesanan, jumlah_produk=jumlah_produk, jumlah_pengguna=jumlah_pengguna, jumlah_pesanan_selesai=jumlah_pesanan_selesai)
    else:
        return redirect(url_for('adlogin'))

@app.route('/adpesanan', methods=['GET', 'POST'])
def adpesanan():
    list_pesanan = list(db.pesanan.find({}))
    return render_template('ad_pesanan.html', list_pesanan=list_pesanan)

@app.route('/update_status/<_id>', methods=['POST'])
def update_status(_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status is None:
        return jsonify({'success': False, 'message': 'Status not provided'}), 400

    result = db.pesanan.update_one(
        {'_id': _id},
        {'$set': {'status': new_status}}
    )

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Record not found'}), 404

    return jsonify({'success': True, 'message': 'Status updated successfully'})

@app.route('/detail_pesanan/<_id>', methods=['GET'])
def detail_pesanan(_id):
    list_pesanan = db.pesanan.find_one({'_id': ObjectId(_id)})
    return render_template('ad_pesanan.html', list_pesanan=list_pesanan)

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
        stock = int(request.form.get('stock'))
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
        stock = int(request.form.get('stock'))
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
    pelanggans = list(db.pembeli.find())
    return render_template('ad_pelanggan.html', pelanggans=pelanggans)

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
        tarif_dalam_kota = float(request.form.get('tarif_dalam_kota'))
        estimasi_dalam_kota = request.form.get('estimasi_dalam_kota')
        tarif_luar_kota = float(request.form.get('tarif_luar_kota'))
        estimasi_luar_kota = request.form.get('estimasi_luar_kota')
        tarif_luar_provinsi = float(request.form.get('tarif_luar_provinsi'))
        estimasi_luar_provinsi = request.form.get('estimasi_luar_provinsi')
        tarif_luar_pulau = float(request.form.get('tarif_luar_pulau'))
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
        tarif_dalam_kota = float(request.form.get('tarif_dalam_kota'))
        estimasi_dalam_kota = request.form.get('estimasi_dalam_kota')
        tarif_luar_kota = float(request.form.get('tarif_luar_kota'))
        estimasi_luar_kota = request.form.get('estimasi_luar_kota')
        tarif_luar_provinsi = float(request.form.get('tarif_luar_provinsi'))
        estimasi_luar_provinsi = request.form.get('estimasi_luar_provinsi')
        tarif_luar_pulau = float(request.form.get('tarif_luar_pulau'))
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
    if (request.args.get('filter')):
        users = list(db.pembeli.find({'nama': {"$regex": u""+ request.args.get('filter') +""}}))
    else:
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
            admin = db.admin.find_one({'_id' : ObjectId(session['user_id'])})
            return render_template('ad_profil.html', admin=admin)
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
    
@app.route('/update_keranjang', methods=['POST'])
def update_keranjang():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        item_id = request.form.get('item_id')
        jumlah = int(request.form.get('jumlah'))

        if jumlah <= 0:
            db.keranjang.delete_one({'_id': ObjectId(item_id), 'user_id': user_id})
        else:
            db.keranjang.update_one(
                {'_id': ObjectId(item_id), 'user_id': user_id},
                {'$set': {'jumlah': jumlah}}
            )

        items_keranjang = list(db.keranjang.find({'user_id': user_id}))
        subtotal = sum(int(item['harga']) * int(item['jumlah']) for item in items_keranjang)

        return jsonify({'status': 'success', 'subtotal': subtotal})

    return jsonify({'status': 'error', 'message': 'Pengguna belum login'})

@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

@app.context_processor
def inject_has_items_and_orders():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        items_keranjang = list(db.keranjang.find({'user_id': user_id}))
        has_items = len(items_keranjang) > 0

        pesanan_list = list(db.pesanan.find({'user_id': user_id, 'status': {'$nin': ['selesai', 'batal']}}))
        has_orders = len(pesanan_list) > 0

        return dict(has_items=has_items, has_orders=has_orders)
    return dict(has_items=False, has_orders=False)

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        pesanan_id = request.form.get('pesanan_id')
        if pesanan_id:
            today = datetime.now()
            mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

            formFile = request.files['formFile']

            extension = formFile.filename.split('.')[-1]
            filename = f'buktiTransfer-{mytime}.{extension}'
            save_to = os.path.join('static/assets/bukti_transfer', filename)        
            formFile.save(save_to)

            db.pesanan.update_one({'_id': pesanan_id}, {'$set': {'bukti_transfer': filename}})
        return redirect(url_for('pesanan'))


@app.route('/pesanan')
def pesanan():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        pesanan_list = list(db.pesanan.find({'user_id': user_id}))

        return render_template('pesanan.html', pesanan_list=pesanan_list)
    else:
        return redirect(url_for('login'))

@app.route('/keranjang')
def keranjang():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        items_keranjang = list(db.keranjang.find({'user_id': user_id}))
        
        for item in items_keranjang:
            produk = db.adproduk.find_one({'_id': ObjectId(item['produk_id'])})
            if produk:
                item['stok'] = produk['stock']
        
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

def order_number(order_id):
    hashed_order_id = hashlib.sha256(order_id.encode()).hexdigest()
    short_order_number = hashed_order_id[:8]
    return short_order_number

def parse_estimasi_pengiriman(estimasi):
    if '-' in estimasi:
        _, end = map(int, estimasi.split('-'))
        return end 
    return int(estimasi)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            user_id = session['user_id']
            nama = session['nama']
            email = session['email']
            telepon = session['telepon']
            
            jalan = request.form.get('jalan')
            rt_rw = request.form.get('rt_rw')
            kelurahan_desa = request.form.get('kelurahan_desa')
            kecamatan = request.form.get('kecamatan')
            provinsi = request.form.get('provinsi')
            kota_kabupaten = request.form.get('kota_kabupaten')
            kode_pos = request.form.get('kode_pos')
            alamat = f"{jalan}, RT/RW: {rt_rw}, Kel/Desa: {kelurahan_desa}, Kec: {kecamatan}, {kota_kabupaten}, {provinsi}, {kode_pos}"

            metode_pengiriman = request.form.get('metode_pengiriman')
            metode_pembayaran = request.form.get('metode_pembayaran')

            pembayaran = db.pembayaran.find_one({'_id': ObjectId(metode_pembayaran)})
            if pembayaran:
                metode_pembayaran = pembayaran['Nama_Bank']
                no_rekening = pembayaran['No_Rek']
                pemilik_rekening = pembayaran['Pemilik_Rek']
            else:
                return redirect(url_for('checkout'))

            items_keranjang = list(db.keranjang.find({'user_id': user_id}))
            subtotal = sum(int(item['harga']) * int(item['jumlah']) for item in items_keranjang)
            total_berat = sum(item['berat'] for item in items_keranjang)

            pengiriman = db.pengiriman.find_one({'jasa_kirim': metode_pengiriman})
            tarif_pengiriman = 0
            estimasi_pengiriman = 0
            if pengiriman:
                for zona, details in pengiriman['zona'].items():
                    if kota_kabupaten in details.get('kota-kabupaten', []):
                        tarif_pengiriman = details['tarif']
                        estimasi_pengiriman = parse_estimasi_pengiriman(details['estimasi'])
                        break

            total_pengiriman = tarif_pengiriman * total_berat
            total_semuanya = float(subtotal) + float(total_pengiriman)

            ringkasan_belanja = []
            for item in items_keranjang:
                produk = db.adproduk.find_one({'_id': ObjectId(item['produk_id'])})
                if produk:
                    ringkasan_belanja.append({
                        'id_produk': str(item['produk_id']),
                        'nama_produk': item['nama_produk'],
                        'jumlah': item['jumlah'],
                        'harga': item['harga'],
                        'gambar': produk['gambar']
                    })

            pesanan_id = str(ObjectId())
            nomor_pesanan = order_number(pesanan_id)

            tanggal_pesanan = datetime.now()
            estimasi_tgl_kirim = tanggal_pesanan
            estimasi_tgl_terima = estimasi_tgl_kirim + timedelta(days=estimasi_pengiriman)

            pesanan = {
                '_id': pesanan_id,
                'nomor_pesanan': nomor_pesanan,
                'user_id': user_id,
                'nama': nama,
                'email': email,
                'telepon': telepon,
                'alamat': alamat,
                'ringkasan_belanja': ringkasan_belanja,
                'metode_pengiriman': metode_pengiriman,
                'total_produk': float(subtotal),
                'total_pengiriman': float(total_pengiriman),
                'total_semuanya': float(total_semuanya),
                'metode_pembayaran': metode_pembayaran,
                'no_rek': no_rekening,
                'pemilik_rek': pemilik_rekening,
                'status': 'pending',
                'estimasi_pengiriman': estimasi_pengiriman,
                'tanggal_pesanan': tanggal_pesanan.strftime('%Y-%m-%d'),
                'estimasi_tgl_kirim': estimasi_tgl_kirim.strftime('%Y-%m-%d'),
                'estimasi_tgl_terima': estimasi_tgl_terima.strftime('%Y-%m-%d')
            }

            db.pesanan.insert_one(pesanan)

             # Update stock
            for item in items_keranjang:
                db.adproduk.update_one(
                    {'_id': ObjectId(item['produk_id'])},
                    {'$inc': {'stock': -int(item['jumlah'])}}
                )

            db.keranjang.delete_many({'user_id': user_id})

            return redirect(url_for('pesanan'))
        
        else:
            user_id = session['user_id']
            items_keranjang = list(db.keranjang.find({'user_id': user_id}))
            subtotal = sum(int(item['harga']) * int(item['jumlah']) for item in items_keranjang)
            pengiriman_list = list(db.pengiriman.find({}))
            pembayaran_list = list(db.pembayaran.find({}))
            return render_template('checkout.html', items_keranjang=items_keranjang, subtotal=subtotal, pengiriman_list=pengiriman_list, pembayaran_list=pembayaran_list)
    else:
        return redirect(url_for('login'))

@app.route('/get_shipping_cost', methods=['POST'])
def get_shipping_cost():
    if request.method == 'POST':
        data = request.get_json()
        kota_kabupaten = data.get('kota_kabupaten')
        berat_total = data.get('berat_total')
        metode_pengiriman = data.get('metode_pengiriman')

        print(f"Received kota_kabupaten: {kota_kabupaten}, berat_total: {berat_total}, metode_pengiriman: {metode_pengiriman}")

        pengiriman = db.pengiriman.find_one({'jasa_kirim': metode_pengiriman})
        if pengiriman:
            print(f"Found pengiriman: {pengiriman}")
            tarif = 0
            for zona, details in pengiriman['zona'].items():
                print(f"Checking zona: {zona}, details: {details}")
                if kota_kabupaten in details.get('kota-kabupaten', []):
                    tarif = int(details['tarif'])
                    print(f"Matched kota_kabupaten: {kota_kabupaten}, tarif: {tarif}")
                    break
            total_tarif = tarif * berat_total
            print(f"Total tarif: {total_tarif}")
            return jsonify({'tarif': total_tarif})
        else:
            print("No matching pengiriman found")

    return jsonify({'tarif': 0})


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
            session['nama'] = user['nama']
            session['email'] = user['email']
            session['telepon'] = user['telepon']
            session['user_id'] = str(user['_id'])
            if 'image' in user:
                session['image'] = user['image']            
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
        session['nama'] = nama
        session['email'] = email
        session['telepon'] = telepon
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
            session['avatar'] = user['avatar'] if 'avatar' in user else None
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
    session.pop('image', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)