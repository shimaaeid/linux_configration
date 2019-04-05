 from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_database import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create  user
User1 = User(name="Esraa Younis", email="esraayounis61@gmail.com")
session.add(User1)
session.commit()

# Items of first category "Men"
category1 = Category(user_id=1, name="Men")

session.add(category1)
session.commit()

item1 = Item(user_id=1, name="Suit", description="Existing all Brands and all styles which fit all occasions.", category=category1)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Shirt & Jacket", description="Existing all Brands and with high quality all made of cotton 100% which suit all purposes work.",
        category=category1)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Shoes", description="Existing all Brands and all types ( Formal , Sports).",
        category=category1)

session.add(item3)
session.commit()


# Items of second category " Women"
category2 = Category(user_id=1, name="Women")

session.add(category2)
session.commit()


item1 = Item(user_id=1, name="Dress", description="Existing all styles and types (Soiree , Normal) which fit all occasions",
                     category=category2)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Cagwal",
                     description=" Contain all styles of clothing for working day , with high quality and fit prices.", category=category2)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Accessories", description="Existing all collections of accessories which add elegance for women ",
            category=category2)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Shoes",
                     description="Existing all Brands and all types (high heel, flat).", category=category2)

session.add(item2)
session.commit()




# Items of third category " Childern"
category3 = Category(user_id=1, name="Childern")

session.add(category3)
session.commit()


item1 = Item(user_id=1, name="Childern Clothes", description="Existing all clothes which fit all ages of childern ",
                     category=category3)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Shoes", description="Existing all shoes which fit all ages of childern and many types and styles ",
               category=category3)

session.add(item2)
session.commit()

print "added items!"
