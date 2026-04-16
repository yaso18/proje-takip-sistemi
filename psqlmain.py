from psql import PostgreSqlDB

# * Veritabanı işlemleri için nesneyi oluşturuyoruz.
db = PostgreSqlDB("python")

# * TÜM veritabanı işlemlerinden önce bağlantı kurulmalıdır.
db.connection()

# * İşlem yapılacak tablo adı
TABLE_NAME = "projes" 
ID_COLUMN = "id" # Otomatik artan ID sütununun adı

# ----------------------------------------------------------------------
# * YAPISAL İŞLEMLER (DDL) VE SIFIRLAMA METOTLARI
# ----------------------------------------------------------------------

# Yeni Veritabanı Oluşturma
# db.create_db("yeni_veritabanim")

# Yeni Tablo Oluşturma
# columns = "id SERIAL PRIMARY KEY, name VARCHAR(100), status BOOLEAN"
# db.create_table(TABLE_NAME, columns)


# 1. TÜM VERİYİ SİL VE SAYACI SIFIRLA (Eski 'truncate_table' yerine)
# ! Bu, ID'nin yeniden 1'den başlamasını sağlar (Tablo içeriği silinir).
# db.reset_table_and_counter(TABLE_NAME)


# 2. SADECE ID SAYACINI SIFIRLA (Veriyi KORUR)
# ! ID atlaması olduğunda sayacı düzeltmek için kullanılır. Veri SİLİNMEZ.
# db.reset_id_counter_only(TABLE_NAME, ID_COLUMN)


# Bir Tabloyu Tamamen Silme
# db.drop_table(TABLE_NAME)

# Bir Veritabanını Tamamen Silme (Dikkatli Kullanın!)
# db.drop_database("yeni_veritabanim")


# ----------------------------------------------------------------------
# * VERİ İŞLEME (CRUD) İŞLEMLERİ
# ----------------------------------------------------------------------


# 1. KAYIT EKLEME (INSERT)
# value = {"name": "Proje A"} # "status": True
# db.insert_record(TABLE_NAME, value)


# 2. KAYIT GÜNCELLEME (UPDATE)
# ! İlk sözlük SET edilecekler, ikinci sözlük WHERE koşuludur.
# update_columns = {"name": "Proje A Güncel", "status": False}
# update_conditions = {"id": 1}
# db.update_record(TABLE_NAME, update_columns, update_conditions)


# 3. TEK KAYIT ÇEKME (SELECT - Tek Satır)
# single_condition = {"id": 1}
# row_data = db.select_row(TABLE_NAME, single_condition)
# if row_data:
#     print(f"Çekilen Tek Kayıt: {row_data}")


# 4. ÇOKLU KAYIT ÇEKME (SELECT - Birden Çok Satır)
# multiple_conditions = {"status": True}
# rows_data = db.select_rows(TABLE_NAME, multiple_conditions)
# if rows_data:
#     print(f"Çekilen Çoklu Kayıtlar: {rows_data}")

# TÜM kayıtları çekme (Koşulsuz)
# all_rows = db.select_rows(TABLE_NAME)
# if all_rows:
#     print(f"Tüm Kayıtlar: {all_rows}")


# 5. KAYIT SİLME (DELETE)
# ! delete: Sadece koşul sözlüğünü kullanarak kaydı siler.
# delete_condition = {"id": 1}
# db.delete(TABLE_NAME, delete_condition)


# ----------------------------------------------------------------------

# ! İşlemler bittikten sonra bağlantıyı kapatmak kaynakları serbest bırakır.
db.disconnect()