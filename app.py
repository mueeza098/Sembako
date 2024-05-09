from dotenv import load_dotenv
load_dotenv()
from flask_bcrypt import Bcrypt

from flask import Flask, request
from models.login import get_username
from models import produk
from models import transaksi
from models import user

from db import conn


from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
get_current_user_id = get_jwt_identity


from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "neuversecretkey"
CORS(app)

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/openapi.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = get_username(username,password)
    if user:
        access_token = create_access_token(identity=user)
        return {'access_token': access_token}, 200
    else:
        return {'message': 'Invalid username or password'}, 401

@app.get('/user')
def get_user():
    return user.get_users()



#CRUD PRODUK


@app.get('/produk')
def get_all_produk():
    with conn.cursor() as cur:
        cur.execute("SELECT id, nama_produk, harga, stok FROM produk ORDER BY harga ASC")
        produks = cur.fetchall()

    list_produk = [{"id": item[0], "nama_produk": item[1], "harga": item[2], "stok": item[3]} for item in produks]

    return list_produk

  

# ini untuk melihat produk menggunakan id
@app.route("/produk/<int:id>", methods=["GET"])
def get_produk_by_id(id):
    item = produk.get_produk_by_id(id)
    if not item:
        return {"message": "Produk tidak ditemukan"}, 404
    return item
   

# ini untuk menghapus produk
@app.delete("/produk/<int:id>")
def delete_produk(id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM produk WHERE id = %s", (id,))
        if cur.rowcount == 0:
            return {"message": "Produk tidak ditemukan"}, 404



# CRUD TRANSAKSI

# Ini adalah endpoint untuk menambahkan data transaksi
@app.post("/transaksi")
def create_transaksi():
    data = request.get_json()
    transaksi.create_new_transaksi(
        alamat=data['alamat'],
        nama=data['nama'],
        kuantitas=data['kuantitas'],
        harga=data['harga'],
        produk_id=data['produk_id'],
        user_id=data['user_id']
    )
    return {"message": "Transaksi berhasil dibuat"}


@app.get('/transaksi')
def get_transaksi():
    return transaksi.get_all_transaksi()


@app.delete("/transaksi/<int:transaksi_id>")
@jwt_required()
def delete_transaksi(transaksi_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM transaksi WHERE id = %s AND user_id = %s RETURNING 1", (transaksi_id, get_jwt_identity()['id']))
        if cur.rowcount == 0:
            return {"message": "Transaksi tidak ditemukan"}, 404

if __name__==('__main__'):
    app.run(debug=True, use_reloader=True, host="0.0.0.0")