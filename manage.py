# from app import create_app

# app = create_app()

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
	return "hello"

# @app.errorhandler(404)
# def error_404(e):
# 	# print(dir(e))
# 	# print(e)
# 	# return "<h2>Ошибка 404, перейдите в корень сайта, должно помочь)</h2>"
# 	return str(e.get_response())

@app.errorhandler(500)
def error_500(e):
	return "<h2>Ошибка 500, перейдите в корень сайта, должно помочь)</h2>"



if __name__ == '__main__':	
	app.run()