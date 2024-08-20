from flask import Flask,request
from flask_restful import Api, Resource, reqparse
from models import db, BookModel
 
app = Flask(__name__)
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
api = Api(app)
db.init_app(app)
 
# push context manually to app
with app.app_context():
    db.create_all()
 
 
class BooksView(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('name',
        type=str,
        required=True,
        help = "Name Can't leave blank"
    )
    parser.add_argument('price',
        type=float,
        required=True,
        help = "Price Can't leave blank"
    )
    parser.add_argument('author',
        type=str,
        required=True,
        help = "Author Can't leave blank"
    )
 
    def get(self):
        books = BookModel.query.all()
        return {'Books':list(x.json() for x in books)}
 
    def post(self):
        #data = request.get_json()
        data = BooksView.parser.parse_args()
 
        new_book = BookModel(data['name'],data['price'],data['author'])
        db.session.add(new_book)
        db.session.commit()
        return new_book.json(),201
 
 
class BookView(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help = "Price Can't leave blank"
        )
    #in your raw json body, you must have to add the author field also, to avoid below error. 
    parser.add_argument('author',
        type=str,
        required=True,
        help = "Author Can't leave blank"
        )
 
    def get(self,name):
        book = BookModel.query.filter_by(name=name).first()
        if book:
            return book.json()
        return {'message':'book not found'},404
 
    def put(self,name):
        #data = request.get_json()
        data = BookView.parser.parse_args()
        
        # Custom validation , the field author must have some value, it should be non empty. 
        if not data['author'].strip():
            return {'message': 'Author cannot be blank'}, 400
        
        book = BookModel.query.filter_by(name=name).first()
 
        if book:
            book.price = data["price"]
            book.author = data["author"]
        #else:
            #book = BookModel(name=name,**data)
 
        db.session.add(book)
        db.session.commit()
 
        return book.json()
 
    def delete(self,name):
        book = BookModel.query.filter_by(name=name).first()
        if book:
            db.session.delete(book)
            db.session.commit()
            return {'message':'Deleted'}
        else:
            return {'message': 'book not found'},404
 
api.add_resource(BooksView, '/books')
api.add_resource(BookView,'/book/<string:name>')
 
app.debug = True
if __name__ == '__main__':
    app.run(host='localhost', port=5000)