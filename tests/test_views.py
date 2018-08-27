# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import unittest
from flask import current_app, url_for
from src import create_app


class CMWTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_health(self):
        response = self.client.get(url_for('.health'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data().decode('utf-8'))
        self.assertTrue(json_response['return'])
        self.assertEqual(json_response['message'], 'All good! :)')

    def test_classify(self):
        true_labels = {}
        true_labels["keyword"] = {1: "Breast Cancer",
                                  2: "Brain Cancer",
                                  3: "Colorectal Cancer",
                                  4: "Kidney Cancer",
                                  5: "Leukemia Cancer",
                                  6: "Lung Cancer",
                                  7: "Melanoma Cancer",
                                  8: "Pancreatic Cancer",
                                  9: "Prostate Cancer"}
        true_labels["partype"] = {1: "Methods",
                                  2: "Introduction",
                                  3: "Abstract",
                                  4: "Results",
                                  5: "Introduction",
                                  6: "Discussion",
                                  7: "Methods",
                                  8: "Abstract",
                                  9: "Results"}
        for label in true_labels:
            print(label)
            for i in true_labels[label]:
                print(i, true_labels[label][i])
                with open("src/assets/example_text_%i.txt" % i) as f:
                    text = f.read().strip()
                response = self.client.post(url_for('.classify', label=label),
                                            content_type='application/json',
                                            data=json.dumps({"text": text}))
                self.assertEqual(response.status_code, 200)
                json_response = json.loads(response.get_data().decode('utf-8'))
                self.assertEqual(json_response["pred_class"], true_labels[label][i])
