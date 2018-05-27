from flask import Blueprint, render_template, session, make_response
from utile.captcha.captcha import captcha

user_blueprint=Blueprint('user',__name__,url_prefix='/user')


@user_blueprint.route('/image_code')
def image_code():
    name, text, buffer = captcha.generate_captcha()

    session['image_code'] = text

    response = make_response(buffer)
    response.mimetype = 'image/png'

    return response
