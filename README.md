## READ ME

1.) open a terminal in the `classifymewhy` folder

2.) install all required packages (assumes an existing uv installation):
```
$ uv sync
```

3.) train & save machine learning model:
```
$ uv run python src/utils.py
```

4.) run local server at `http://127.0.0.1:8000` and to test the app in the browser:
```
$ uv run uvicorn src.main:app --reload
```

5.) send a post request with some data to `http://127.0.0.1:8000/classify`, for example using the `test_classify.py` script in the `classifymewhy/tests` folder:
```
$ uv run python tests/test_classify.py
```
