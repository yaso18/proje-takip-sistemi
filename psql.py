import psycopg2
from psycopg2.extras import register_hstore
from psycopg2 import sql 

class PostgreSqlDB:
    def __init__(self, database):
        # ! Bağlantı Bilgileri (Sizin bilgileriniz)
        self.__host = "localhost"
        self.__user = "postgres"
        self.__password = "Yf25072013"
        self.__port = "5432"
        self.__database = database
        self.__connection = None
        self.__cursor = None

    def connection(self):
        try:
            self.__connection = psycopg2.connect(
                dbname=self.__database,
                user=self.__user,
                password=self.__password,
                host=self.__host,
                port=self.__port
            )
            self.__cursor = self.__connection.cursor()
            register_hstore(self.__connection)
            print("✅ PostgreSQL veritabanına bağlanıldı.")
        except psycopg2.Error as e:
            print(f"❌ Bağlantı başarısız oldu: {e}")
            self.__connection = None
            self.__cursor = None
    
    # ------------------------------------------------------------------
    # # DDL VE DB YÖNETİM METOTLARI
    # ------------------------------------------------------------------

    def create_table(self, table_name, columns):
        try:
            self.__cursor.execute(sql.SQL(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"))
            self.__connection.commit()
            print(f"✅ {table_name} tablosu oluşturuldu veya zaten mevcut.")
        except psycopg2.Error as e:
            print(f"❌ Tablo oluşturma hatası: {e}")
            self.__connection.rollback()
    
    # ------------------------------------------------------------------
    # # CRUD METOTLARI
    # ------------------------------------------------------------------

    def insert_record(self, table_name, data):
        """Tek bir kayıt ekler. Kullanım: db.insert_record(\"tablo\", {\"name\": \"Proje A\", \"status\": True})"""
        columns = data.keys()
        values_placeholders = ', '.join(['%s'] * len(data))
        
        sql_query = sql.SQL(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values_placeholders})")
        values = tuple(data.values())
        
        try:
            self.__cursor.execute(sql_query, values)
            self.__connection.commit()
            print(f"✅ {table_name} adlı tabloya kayıt eklendi.")
        except psycopg2.Error as e:
            print(f"❌ Kayıt ekleme hatası: {e}")
            self.__connection.rollback()

    def update_record(self, table_name, update_data, conditions):
        """Kaydı günceller. Kullanım: db.update_record(\"tablo\", {\"status\": True}, {\"id\": 1})"""
        set_clause = ", ".join([f"{key}=%s" for key in update_data.keys()])
        where_clause = " AND ".join([f"{key}=%s" for key in conditions.keys()])
        
        sql_query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = tuple(list(update_data.values()) + list(conditions.values()))
        
        try:
            self.__cursor.execute(sql_query, values)
            self.__connection.commit()
            print(f"✅ {table_name} adlı tablonun {conditions} koşullu kaydı güncellendi.")
        except psycopg2.Error as e:
            print(f"❌ Kayıt güncelleme hatası: {e}")
            self.__connection.rollback()
    
    def delete_record(self, table_name, conditions):
        """Kaydı siler. Kullanım: db.delete_record(\"tablo\", {\"id\": 1})"""
        # ✅ KRİTİK DÜZELTME: Sözdizimi hatası giderildi.
        where_clause = " AND ".join([f"{key}=%s" for key in conditions.keys()]) 
        sql_query = f"DELETE FROM {table_name} WHERE {where_clause}"
        values = tuple(conditions.values())
        
        try:
            self.__cursor.execute(sql_query, values)
            self.__connection.commit()
            print(f"✅ {table_name} adlı tablodan 1 kayıt silindi.")
        except psycopg2.Error as e:
            print(f"❌ Kayıt silme hatası: {e}")
            self.__connection.rollback()
            
    def select_row(self, table_name, conditions=None):
        """Koşula uygun tek bir kayıt çeker. Kullanım: db.select_row(\"tablo\", {\"id\": 1})"""
        if not conditions:
            print("Hata: Tek bir kayıt çekmek için koşul (conditions) gereklidir.")
            return None

        where_clause = " AND ".join([f"{key}=%s" for key in conditions.keys()])
        sql_query = f"SELECT * FROM {table_name} WHERE {where_clause}"
        values = tuple(conditions.values())
        
        self.__cursor.execute(sql_query, values)
        # PostgreSQL'de fetchone bir tuple döndürür.
        row = self.__cursor.fetchone() 
        
        if not row:
            print(f"⚠️ {table_name} tablosunda koşullara uygun tek bir kayıt bulunamadı.")
        return row
        
    def select_rows(self, table_name, conditions=None):
        """Birden çok kayıt çeker. Kullanım: db.select_rows(\"tablo\", {\"status\": \"active\"}) veya db.select_rows(\"tablo\")"""
        sql_query = f"SELECT * FROM {table_name} ORDER BY id DESC" # Yeni eklenenler üstte gözüksün
        values = ()

        if conditions:
            where_clause = " AND ".join([f"{key}=%s" for key in conditions.keys()])
            sql_query += f" WHERE {where_clause}"
            values = tuple(conditions.values())

        self.__cursor.execute(sql_query, values)
        rows = self.__cursor.fetchall()
        
        if not rows:
            print(f"⚠️ {table_name} tablosunda kayıt bulunamadı.")
        return rows

    # ------------------------------------------------------------------
    # # YÖNETİM METOTLARI
    # ------------------------------------------------------------------

    def reset_id_on_delete(self, table_name, id_column="id"):
        """Bir kayıt silindikten sonra ID sayacını (sequence) en yüksek mevcut ID'ye ayarlar."""
        
        if not self.__connection:
            print("Hata: Veritabanı bağlantısı kapalı veya kurulmamış.")
            return False

        try:
            # Önce en büyük ID'yi bul
            self.__cursor.execute(sql.SQL(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name}"))
            max_id = self.__cursor.fetchone()[0]
            
            # Sayacı (sequence) bu ID'ye göre ayarla
            sequence_name = f"{table_name}_{id_column}_seq" 
            
            # setval fonksiyonunu kullanarak sayacı ayarla
            self.__cursor.execute(sql.SQL(f"SELECT setval('{sequence_name}', %s, COALESCE((SELECT MAX({id_column}) FROM {table_name}) IS NOT NULL, FALSE))"), (max_id,))
            
            self.__connection.commit()
            print(f"✅ {table_name} tablosunun ID sayacı {max_id + 1} olarak ayarlandı.")
            return True
        except psycopg2.Error as e:
            print(f"❌ ID sayacını sıfırlama hatası: {e}")
            self.__connection.rollback()
            return False
        
    def restart_identity_to_one(self, table_name: str, id_column: str = "id"):
        """
        DİKKAT: Tablodaki veriyi silmeden, ID sayacını (sequence) zorla 1'den
        başlayacak şekilde sıfırlar. Bu metod, tablo boşken ID'nin 1'den
        başlaması için kullanılır. Tabloda veri varsa PRIMARY KEY ihlaline
        (çakışmaya) yol açabilir.
        
        Args:
            table_name (str): ID sayacı sıfırlanacak tablo adı.
            id_column (str): ID sütununun adı (Varsayılan: "id").
        """
        
        if not self.__connection:
            print("Hata: Veritabanı bağlantısı kapalı veya kurulmamış.")
            return False

        try:
            # Sequence adını oluştur (Örn: projets_id_seq)
            sequence_name = f"{table_name}_{id_column}_seq" 

            # setval(sequence_name, next_value, is_called)
            # next_value = 1, is_called = false -> bir sonraki nextval çağrısı 1 döner.
            sql_command = sql.SQL("SELECT setval(%s, 1, false)")
            
            self.__cursor.execute(sql_command, (sequence_name,))
            
            self.__connection.commit()
            print(f"✅ {table_name} tablosunun ID sayacı başarıyla 1'den başlayacak şekilde sıfırlandı.")
            return True
        except psycopg2.ProgrammingError as e:
            if "does not exist" in str(e):
                print(f"❌ Hata: Sequence adı bulunamadı. ({sequence_name}). Tablo adını ve sütun adını kontrol edin.")
            else:
                print(f"❌ ID sayacını sıfırlama hatası: {e}")
            self.__connection.rollback()
            return False
        except psycopg2.Error as e:
            print(f"❌ ID sayacını sıfırlama hatası: {e}")
            self.__connection.rollback()
            return False
        
    def disconnect(self):
        if self.__cursor:
            self.__cursor.close()
            self.__cursor = None
        if self.__connection:
            self.__connection.close()
            self.__connection = None
            print("✅ PostgreSQL veritabanı bağlantısı kesildi.")
# Kodu buraya kadar kopyalayın.