from flask import Flask, request, jsonify
from models.user import User
from database import db
import bcrypt
from flask_login import (
    LoginManager,
    login_user,
    current_user,
    logout_user,
    login_required,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud"
)


login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# view login - pega a rota
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data.get("password")

    if username and password:
        # Aqui ele retorna todas as informações de user
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user)
            return jsonify({"message:": "Autenticado com sucesso"})

    return jsonify({"message:": "Credenciais inválidas"}), 400


# Para acessar essa rota, o usuario ja deve estar logado...
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message:": "Logout realizado com sucesso"})


@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt(14))
        user = User(username=username, password=hashed_password, role="user")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso"})

    return jsonify({"message": "Dados invalidos"}), 400


@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return jsonify({"username": user.username})

    return jsonify({"message": "Usuário não encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    # print(f"Current user id: {current_user.id}, role: {current_user.role}")

    if id_user != current_user.id and current_user.role == "user":
        return jsonify({"message": "Operação não permitida"}), 403

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} alterado com sucesso"})

    return jsonify({"message": "Usuário não encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != "admin":
        return jsonify({"message": "Operação não permitida"}), 403

    if id_user == current_user.id:
        return jsonify({"message": "Deleção não permitida"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} deletado com sucesso"})

    return jsonify({"message": "Usuário não encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
