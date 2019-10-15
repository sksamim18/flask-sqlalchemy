from app import db


class Prescription(db.Model):

    __tablename__ = 'prescription'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient = db.relationship('User', foreign_keys=[patient_id])
    timestamp = db.Column(db.DateTime)

    def __str__(self):
        return 'DoctorID: {} PatientID {}'.format(doctor_id, patient_id)


class Diagnosis(db.Model):

    __tablename__ = 'diagnosis'
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey(
        'prescription.id'), nullable=False)
    prescription = db.relationship(
        'Prescription', foreign_keys=[prescription_id])
    cause = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return 'PrescriptionID: {} Cause {}'.format(
            self.prescription_id, self.cause)


class Treatment(db.Model):

    __tablename__ = 'treatment'
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(
        db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    prescription = db.relationship(
        'Prescription', foreign_keys=[prescription_id])
    medication = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return 'PrescriptionID: {} Medication {}'.format(
            self.prescription_id, self.medication)
