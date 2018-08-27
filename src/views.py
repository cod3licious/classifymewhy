#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import random
from flask import jsonify, make_response, abort, current_app, request, render_template

from .utils import classify_me_why
from . import blueprint


@blueprint.before_request
def setup_request():
    if not current_app.testing:
        # authenticate by using a custom key
        allowed = True
        # try with custom key
        if current_app.config['SECRET_KEY'] == request.args.get('secret_key'):
            allowed = True
        if not allowed:
            abort(403)


@blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'return': False, 'error': ['Not found']}), 404)


@blueprint.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'return': False, 'error': ['Forbidden']}), 403)


@blueprint.errorhandler(400)
def missing_data(error):
    return make_response(jsonify({'return': False, 'error': ['Missing data']}), 400)


@blueprint.route('/health')
def health():
    return make_response(jsonify({'return': True, 'message': 'All good! :)'}), 200)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    # load a random example text
    with open("src/assets/example_text_%i.txt" % random.randint(1, 9)) as f:
        example_text = f.read().strip()
    if request.method == 'POST':
        text = request.form.get('text', '')
        label = request.form.get('label', '')
        if not text:
            return render_template('index.html', example_text=example_text, pred_class="-", pred_score=0., text_div="ERROR: You have to enter some text below...")
        # classify text
        pred_class, pred_score, htmlstr = classify_me_why(text, label)
        return render_template('index.html', example_text=example_text, pred_class=pred_class, pred_score=pred_score, text_div=htmlstr)
    return render_template('index.html', example_text=example_text)


@blueprint.route('/classify', methods=['POST'])
def classify():
    try:
        post_data = request.get_json()
    except:
        abort(400)
    text = post_data.get('text', '')
    if not text:
        return make_response(jsonify({"return": False, "error": ["no text provided"]}), 400)
    label = request.args.get('label', 'keyword')
    # classify text
    pred_class, pred_score, htmlstr = classify_me_why(text, label)
    return make_response(jsonify({"pred_class": pred_class, "pred_score": pred_score, "text_div": htmlstr}), 200)
