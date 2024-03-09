from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def __repr__(self):
        return f'< Cafe {self.name}>'

    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "map_url":self.map_url,
            "image_url":self.img_url,
            "location":self.location,
            "seats":self.seats,
            "toilets":self.has_toilet,
            "wifi":self.has_wifi,
            "sockets":self.has_sockets,
            "calls":self.can_take_calls,
            "coffee_price":self.coffee_price
        }


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record
@app.route("/random", methods=["GET","POST"])
def get_random_cafe():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())
    

@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()

    return jsonify(cafes =[cafe.to_dict() for cafe in all_cafes] )

@app.route("/search")
def search_a_cafe():
    cafe_location = request.args.get('loc')
    print(cafe_location)
    try:
        result = db.session.execute(db.select(Cafe).where(Cafe.location == cafe_location))
        all_cafes = result.scalars().all()
    except:
        err_msg = { "Not Found": "We dont have a cafe at that location"}
        return jsonify(error = err_msg)
    else:
        return jsonify(cafes =[cafe.to_dict() for cafe in all_cafes] )

# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

# HTTP PUT/PATCH - Update Record

@app.route("/update_price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    print("Its here")
    new_price = request.args.get("new_price")
    print(new_price)
    try:
        cafe = db.get_or_404(Cafe, cafe_id)
    except:
        err_msg = { "Not Found":"Cafe with that ID not found in the database"}
        return jsonify(error= err_msg)
    else:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
