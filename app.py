import os
from typing import TYPE_CHECKING
from typing import List
from pydantic import BaseModel
from flask import Flask, jsonify, redirect, request, url_for
from lcovparse import lcovparse
from http import HTTPStatus
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
db = SQLAlchemy()
app.config["FLASK_SECRET"] = "s*&88ssridayISfifd&DFS67aslmy4lmi$LMy24l9m"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "db.sqlite"
)
db = SQLAlchemy(app)

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model

    DBBaseModel = db.make_declarative_base(Model)
else:
    DBBaseModel = db.Model


@app.get("/<user_id>")
def get_files_for_user(user_id):
    files = db.session.execute(
        db.select(DBFileCoverage).order_by(DBFileCoverage.file_path)
    ).scalars()

    return jsonify([s.serialize() for s in files.all()])


@app.route("/<user_id>/<commit_sha>")
def index(user_id, commit_sha):
    if request.method == "POST":
        file = request.files["file"]
        if file:
            coverage_data = lcovparse(file.stream.read().decode())
            for coverage_file in coverage_data:
                cov_model = DBFileCoverage(
                    missing_lines=",".join([str(l.line) for l in coverage_file.miss]),
                    commit_sha=commit_sha,
                    user_id=user_id,
                    file_path=coverage_file.file_name,
                )
                db.session.add(cov_model)
            db.session.commit()
            return redirect(url_for("index", user_id="a", commit_sha="b"))
        else:
            return {
                "error": "no file uploaded",
                "status": HTTPStatus.BAD_REQUEST,
            }, HTTPStatus.BAD_REQUEST
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="/naman/abcd1234" method="post" enctype="multipart/form-data">
        <p><input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    """


class DBFileCoverage(DBBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, nullable=False)
    commit_sha = db.Column(db.String, nullable=False)
    file_path = db.Column(db.String, nullable=False)
    missing_lines = db.Column(db.String, nullable=False)

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}


class FileCoverage(BaseModel):
    commit_sha: str
    lines_missing: List[int]


class File(BaseModel):
    reports: List[FileCoverage]
    tree_sha: str
    file_path: str


class RepositoryReport(BaseModel):
    files: List[str]
    sha: str


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    i = inspect(DBFileCoverage)
    attr_names = [c_attr.key for c_attr in i.mapper.column_attrs]
    print(attr_names)
    app.run(host="0.0.0.0", port=8080, debug=True)
