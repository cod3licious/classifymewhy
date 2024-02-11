## READ ME

1.) open a terminal in the `classifymewhy` folder

2.) install all required packages and activate Python virtual env (assumes an existing python 3 and poetry installation):
```
$ poetry install --no-root
$ poetry shell
```

3.) train & save machine learning model:
```
$ python src/utils.py
```

4.) run local server at `http://127.0.0.1:8000`:
```
$ uvicorn src.main:app --reload
```

5.) send a post request with some data to `http://127.0.0.1:8000/classify`, for example using the `test_classify.py` script in the `classifymewhy/tests` folder:
```
$ python tests/test_classify.py
```
