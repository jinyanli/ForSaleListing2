db = DAL("sqlite://storage.sqlite")

from gluon.tools import Auth
auth = Auth(db)
auth.define_tables(username=True)

db.define_table('forsale',
                Field('seller_name'),
                Field('user_id', db.auth_user),
                Field('phone'),
                Field('email'),
                Field('category'),
                Field('date_posted', 'datetime',default=request.now,writable=False),
                Field('title'),
                Field('image','upload'),
                Field('price','double'),
                Field('sold','boolean'),
                Field('description', 'text'),
                Field('votes', 'integer', readable=False, writable=False, default=0)
                )

db.define_table('imageList',
  Field('forsale_id', 'reference forsale', readable=False , writable=False),
  Field('image', 'upload'))

CATEGORY = ['Car', 'Bike', 'Book', 'Music',' Outdoors', 'Household', 'Misc']

db.forsale.price.requires = IS_FLOAT_IN_RANGE(0, 100000.0,
                             error_message='The price should be in the range 0..100000')
db.forsale.id.readable = False
db.forsale.sold.default = False
db.forsale.description.label = 'Item Description'
db.forsale.user_id.default = auth.user_id
db.forsale.user_id.writable = db.forsale.user_id.readable = False
db.forsale.email.requires = IS_EMAIL()
db.forsale.phone.requires=IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',error_message='not a phone number')
db.forsale.category.requires = IS_IN_SET(CATEGORY)
db.forsale.category.default = 'Misc'
db.forsale.category.required = True
