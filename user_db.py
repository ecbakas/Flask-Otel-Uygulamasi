# This file contains an example Flask-User application.
# To keep the example simple, we are applying some unusual techniques:
# - Placing everything in one file
# - Using class-based configuration (instead of file-based configuration)
# - Using string-based templates (instead of file-based templates)

import datetime
from flask import Flask, request, render_template_string, render_template,url_for,redirect
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin, user_logged_in, user_logged_out
from sqlalchemy.sql import table, column, select 
from sqlalchemy import MetaData
from wtforms import ValidationError
from sqlalchemy import update

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
    
    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings 
    # #USER_ENABLE_EMAIL=True ise bu ayarları yapın. Google güvenlik ayarları bu işlemi yapmanıza izin vermeyebilir.
    #Detaylı bilgiyi https://support.google.com/accounts/answer/6010255?p=lsa_blocked&hl=en-GB&visit_id=636759033269131098-410976990&rd=1 dan edinebilirsiniz. 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'ecbakas@gmail.com' # gmail adresinizi girin
    MAIL_PASSWORD = '151703453a' # gmail şifrenizi girin
    MAIL_DEFAULT_SENDER = '"MyApp" <xyz@gmail.com>'

    # Flask-User settings
    USER_APP_NAME = "Web Sitesi"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
   # Daha detaylı bilgi https://flask-user.readthedocs.io/en/latest/configuring_settings.html de bulunabilir.
def create_app():
    """ Flask application factory """
    
    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Initialize Flask-BabelEx
    babel = Babel(app)
    # Initialize Flask-SQLAlchemy
    @babel.localeselector
    def get_locale():
       translations = [str(translation) for translation in babel.list_translations()]
    #   return request.accept_languages.best_match(translations)
    # @babel.localeselector
    #def get_locale():
    #   if request.args.get('lang'):
    #       session['lang'] = request.args.get('lang')
    #       return session.get('lang', 'tr')

    db = SQLAlchemy(app)
 

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
   
    class User(db.Model, UserMixin):
     
    
        def allowed(self, access_level):
            return self.access >= access_level
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')

        # User information
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

        # Define the relationship to Role via UserRoles
        roles = db.relationship('Role', secondary='user_roles')
    # Define the Role data-model

    class Gonderi(db.Model):
        __tablename__ = 'gonderiler'
        id = db.Column(db.Integer, autoincrement=True, primary_key=True)
        baslik=db.Column(db.String(40))
        baslikk=db.Column(db.String(40))        
        govde = db.Column(db.String(140))
        timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
        user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    class Otel(db.Model):
        __tablename__ = 'Otel'
        id = db.Column(db.Integer, autoincrement=True, primary_key=True)
        otel=db.Column(db.String(40)) 
        otelpuan=db.Column(db.String(40)) 
        otelf=db.Column(db.String(40)) 

    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
        
    
    class Sepet:
        urunler={}
    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # Create all database tables
    db.create_all()
    engine = create_engine('sqlite:///basic_app.sqlite')
    meta = MetaData(engine,reflect=True)
    table = meta.tables['gonderiler']
    table_otel = meta.tables['Otel']

    @user_logged_in.connect_via(app)
    def _after_login_hook(sender, user, **extra):
        sender.logger.info('user logged in')
        global sepet
        sepet=Sepet()

    
    @user_logged_out.connect_via(app)
    def _after_logout_hook(sender, user, **extra):
        sender.logger.info('user logged out')
        #global sepet
        #del sepet
    
    # Create 'member@example.com' user with no roles
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(
            email='member@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()
    
    if not User.query.filter(User.email == 'member1@example.com').first():
        user = User(
            email='member1@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()
    
    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            email='admin@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    # The Home page is accessible to anyone
    @app.route('/')
    def home_page():
        return render_template('anasayfa.html')

    @app.route('/sepet_islemleri', methods = ['POST', 'GET'])  # /otel_ekle rotasını oluşturuyoruz,post ve get metotlarını kullanacağımızı belirtiyoruz.
    @login_required    # Kullanıcı girişi gerekli tanımlamasını yapıyoruz.
    def sepet_islemleri():
        global sepet   #sepet değişkenini tanımlıyoruz.      
        sepet=Sepet() #sepet değişkenimizi Sepet() Class'ına eşitliyoruz.
        db_uri =  'sqlite:///basic_app.sqlite' # SQLITE Bağlantımız.
        engine = create_engine(db_uri) #db_uri çalıştırıyoruz.
        conn = engine.connect() # Bağlantıyı açıyoruz.
              
        if request.method == 'POST': # If bloku ile çağırılan metodun metodunun 'POST' olma durumunu kontrol ediyoruz.  
            try:
                oid = request.form['otelID'] #Bağlantılı html sayfasından name='otelID' olan içeriği oid değişkenine atıyoruz.
                qry = db.session.query(Otel).filter(Otel.id==oid).all() # qry isimli sorgu oluşturuyoruz ve bu sorguda Otel tablosunun 'otelid'si oid değişkenimize eşit olanı çekiyoruz.
                sepet.urunler[oid]=qry # 1-1 indexe oid 1-2 indexe qry sorgumuzu atıyoruz
            except: # Olası hatalar için except bloku.
                msg = "Otel ekleme işlemi sırasında hata oluştu"                        
        return render_template('/sepeti_gor.html', sepet_ici=sepet.urunler) # 'sepeti_gor.html' template'ini sepet_ici=sepet.urunler atamasıyla geri döndürüyoruz.

    @app.route('/admin_page')
    @roles_required('Admin') #Use of @roles_required decorator
    def admin_page():
        return render_template('anasayfa-admin.html')

    #------------------------------------------------------------------#
    @app.route('/otel_sayfasi') # /otel_sayasi roasını oluşturuyoruz.
    @roles_required('Admin') # 'Admin' rolü gerekli tanımlamasını yapıyoruz.
    def otel_sayfasi():
        return render_template('otel-ekle.html') # 'otel-ekle.html' template'ini geri döndürüyoruz.
    
    
    @app.route('/otel_ekle', methods = ['POST', 'GET']) # /otel_ekle rotasını oluşturuyoruz,post ve get metotlarını kullanacağımızı belirtiyoruz.
    @roles_required('Admin') # 'Admin' rolü gerekli tanımlamasını yapıyoruz.
    def otel_ekle():
        if request.method == 'POST': # If bloku ile çağırılan metodun metodunun 'POST' olma durumunu kontrol ediyoruz.  
            try:
                otel = request.form['otel'] #Bağlantılı html sayfasından name='otel' olan içeriği otel değişkenine atıyoruz.
                otelPu = request.form['otelP']  #Bağlantılı html sayfasından name='otelP' olan içeriği otelPu değişkenine atıyoruz.
                otelFi = request.form['otelF']   #Bağlantılı html sayfasından name='otelF' olan içeriği otelFi değişkenine atıyoruz.
                
                otelE = Otel( # otelE değişkeninde 'Otel' tablosunun otel,otelpuan,otelf alanlarına çektiğimiz verileri giriyoruz.
                    otel=otel,otelpuan=otelPu,otelf=otelFi
                    )  
                db.session.add(otelE)  #otelE değişkenini veritabanımıza ekliyoruz.
                db.session.commit()
                msg = "Otel başarı ile eklendi" 
            except:   # Olası hatalar için except bloku.
                msg = "Otel ekleme işlemi sırasında hata oluştu"
             
            finally:   # Her iki koşulda da çalışacak blok.
                return render_template("otel-ekle.html", msg = msg)
   
   
    @app.route('/otel_listele')
    def otel_listele():
        db_uri =  'sqlite:///basic_app.sqlite'
        engine = create_engine(db_uri)
        conn = engine.connect()
        selectt =db.select([table_otel.c.id,table_otel.c.otel,table_otel.c.otelpuan,table_otel.c.otelf])
        rows = conn.execute(selectt)
        return render_template("otel_listele.html", rows =rows)
   
   
    @app.route('/otel_listele_admin')
    def otel_listele_admin():
        db_uri =  'sqlite:///basic_app.sqlite'
        engine = create_engine(db_uri)
        conn = engine.connect()
        selectt =db.select([table_otel.c.id,table_otel.c.otel,table_otel.c.otelpuan,table_otel.c.otelf])
        rows = conn.execute(selectt)
        return render_template("otel_listele_admin.html", rows =rows)
    
    
    @app.route('/otel_sil', methods = ['POST', 'GET'])
    @roles_required('Admin')
    def otel_sil():
        db_uri =  'sqlite:///basic_app.sqlite'
        engine = create_engine(db_uri)
        conn = engine.connect()
        selectt =db.select([table_otel.c.id,table_otel.c.otel,table_otel.c.otelpuan,table_otel.c.otelf])
        rows = conn.execute(selectt)
        if request.method == 'POST':
            try:
                otelid = request.form['otelID']
                del_st = table_otel.delete().where(table_otel.c.id == otelid)                
                res = conn.execute(del_st)
                sel_st =table_otel.select()
                msg = "otel başarı ile silindi"
            except:
                msg = "otel silme işlemi sırasında hata oluştu"
            finally:
                return redirect(url_for('otel_sil'))
        return render_template("otel_sil.html", rows =rows)
    
    
    @app.route('/otel_sil_hepsi', methods = ['POST', 'GET'])
    @roles_required('Admin')
    def otel_sil_hepsi():

        db_uri =  'sqlite:///basic_app.sqlite'
        engine = create_engine(db_uri)
        conn = engine.connect()
        selectt =db.select([table_otel.c.id,table_otel.c.otel,table_otel.c.otelpuan,table_otel.c.otelf])
        rows = conn.execute(selectt)
        if request.method == 'POST':
            try:
                del_st = table_otel.delete()
                res = conn.execute(del_st)
                msg = "otel başarı ile silindi"
            except:
                msg = "otel silme işlemi sırasında hata oluştu"
            finally:
                return redirect(url_for('otel_sil'))
        return render_template("otel_sil.html", rows =rows)
    
    
    @app.route('/otel_guncelle', methods = ['POST', 'GET'])
    @roles_required('Admin')
    def otel_guncelle():

        db_uri =  'sqlite:///basic_app.sqlite'
        engine = create_engine(db_uri)
        conn = engine.connect()
        selectt =db.select([table_otel.c.id,table_otel.c.otel,table_otel.c.otelpuan,table_otel.c.otelf])
        rows = conn.execute(selectt)
        if request.method == 'POST':
            try:
                oid = request.form['id']
                otelY = request.form['otelY']
                otelFiyat = request.form['otelYF']
                otelPuan = request.form['otelYP']              
                upt_st = update(table_otel).where(table_otel.c.id==oid).values(otel=otelY,otelf=otelFiyat,otelpuan=otelPuan)
                res = conn.execute(upt_st)
                msg = "otel başarı ile güncellendi"
            except:
                msg = "otel güncelleme işlemi sırasında hata oluştu"
            finally:
                return redirect('otel_guncelle')
        return render_template("otel_guncelle.html", rows =rows)

    return app
  
# Start development web  server
if __name__ == '__main__':
    app = create_app()
   # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True)
