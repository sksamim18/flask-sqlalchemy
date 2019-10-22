from app import db

from sqlalchemy_utils import generic_relationship


class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(100))
    first_name = db.Column(db.String(32))
    middle_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    password = db.Column(db.String, nullable=False)

    @property
    def phone_number(self):
        return self.username

    def __str__(self):
        return 'UserID: {}, Phone number: {}'.format(
            self.id, self.phone_number)


class UserMapping(db.Model):

    __tablename__ = 'user_mappings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id])
    entity_type = db.Column(db.String(255))
    entity_id = db.Column(db.Integer)
    entity = generic_relationship(entity_type, entity_id)
    __table_args__ = (db.UniqueConstraint(user_id, entity_type),)

    def __str__(self):
        return 'UserID: {}, UserType: {}'.format(
            self.parent_id, self.object_type)


class Doctor(db.Model):

    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100))
    qualification = db.Column(db.String(100), nullable=False)
    work_ex = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String)
    account_status = db.Column(db.String, default="active")

    def __str__(self):
        return 'Address:{}, Qualification: {}'.format(
            self.address, self.qualification)


class Pharmacist(db.Model):

    __tablename__ = 'pharmacist'
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(100))
    cerification = db.Column(db.String(100), nullable=False)
    work_ex = db.Column(db.Integer, nullable=False)
    opening_time = db.Column(db.String)
    closing_time = db.Column(db.String)
    address = db.Column(db.String)
    account_status = db.Column(db.String, default="active")

    def __str__(self):
        return 'Shop name: {}, address: {}'.format(
            self.shop_name, self.address)


class Patient(db.Model):

    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    dob = db.Column(db.DateTime)
    address = db.Column(db.String)
    gender = db.Column(db.String, default='M')

    def __str__(self):
        return 'Dob: {} gender: {}'.format(self.dob, self.gender)


class AuthToken(db.Model):

    __tablename__ = 'auth_token'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user = db.relationship('User', foreign_keys=[user_id])
    token = db.Column(db.String)
    user_type = db.Column(db.String)
    __table_args__ = (db.UniqueConstraint(user_id, user_type),)

    def __str__(self):
        return 'UserID: {}, Token: {}'.format(self.user_id, self.token)
