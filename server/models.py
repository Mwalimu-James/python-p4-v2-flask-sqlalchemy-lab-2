from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    # Relationship with Review model
    reviews = db.relationship('Review', back_populates='customer')
    items = association_proxy('reviews', 'item')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reviews': [review.to_dict() for review in self.reviews]
        }

class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    
    # Relationship with Review model
    reviews = db.relationship('Review', back_populates='item')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'reviews': [review.to_dict() for review in self.reviews]
        }

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    
    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    @validates('comment')
    def validate_comment(self, key, comment):
        if not comment or len(comment) > 255:
            raise ValueError("The comment must be between 1 and 255 characters.")
        return comment

    @classmethod
    def find_by_customer(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id).all()

    def to_dict(self):
        return {
            'id': self.id,
            'comment': self.comment,
            'customer_id': self.customer_id,
            'item_id': self.item_id,
            'customer': self.customer.name if self.customer else None,
            'item': self.item.name if self.item else None
        }

    def __repr__(self):
        return f"<Review(id={self.id}, comment='{self.comment}', customer_id={self.customer_id}, item_id={self.item_id})>"
