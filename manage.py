from app import create_app

app = create_app()

@app.errorhandler(404)
def error_404(e):
	return "<h2>Ошибка 404, перейдите в корень сайта, должно помочь)</h2>"

@app.errorhandler(500)
def error_500(e):
	return "<h2>Ошибка 500, перейдите в корень сайта, должно помочь)</h2>"



if __name__ == '__main__':	
	app.run(debug=True, port=80, host="0.0.0.0")