import re

import joblib
import matplotlib as mpl
import numpy as np
from matplotlib.cm import get_cmap
from scipy.sparse import csr_matrix, lil_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def scores2html(text, scores, preprocess_text=lambda x: x, highlight_oov=False):
    """
    Based on the original text and relevance scores, generate a html doc highlighting positive / negative words

    Inputs:
        - text: the raw text in which the words should be highlighted
        - scores: a dictionary with {word: score} or a list with tuples [(word, score)]
        - preprocess_text: function to preprocess the text to match them to the tfidf features (needed if scores is a dict)
        - highlight_oov: if True, out-of-vocabulary words will be highlighted in yellow (default False)

    Returns:
        - string with the html text
    """
    # colormaps
    cmap_pos = get_cmap("Greens")
    cmap_neg = get_cmap("Reds")
    norm = mpl.colors.Normalize(0.0, 1.0)

    # normalize score by absolute max value
    if isinstance(scores, dict):
        N = np.max(np.abs(list(scores.values())))
        scores_dict = {word: scores[word] / N for word in scores}
        # transform dict into word list with scores
        scores = [(word, scores_dict.get(preprocess_text(word))) for word in re.findall(r"(?u)\b\w\w+\b", text, re.UNICODE)]
    else:
        N = np.max(np.abs([t[1] for t in scores if t[1] is not None]))
        scores = [(w, s / N) if s is not None else (w, None) for w, s in scores]

    # TODO: would probably be more efficient if resttext wasn't constantly overwritten
    htmlstr = ['<div style="white-space: pre-wrap; font-family: monospace;">']
    resttext = text
    for word, score in scores:
        # was anything before the identified word? add it unchanged to the html
        htmlstr.append(resttext[: resttext.find(word)])
        # cut off the identified word
        resttext = resttext[resttext.find(word) + len(word) :]
        # get the colorcode of the word
        rgbac = (1.0, 1.0, 0.0)  # for unknown words
        alpha = 0.3 if highlight_oov else 0.0
        if score is not None:
            rgbac = cmap_neg(norm(-score)) if score < 0 else cmap_pos(norm(score))
            alpha = 0.5
        htmlstr.append(
            f'<span style="background-color: rgba({round(255 * rgbac[0])}, {round(255 * rgbac[1])}, {round(255 * rgbac[2])}, {alpha:.1f})">{word}</span>'
        )
    # after the last word, add the rest of the text
    htmlstr.append(resttext)
    htmlstr.append("</div>")
    return "".join(htmlstr)


def classify_me_why(text, label="keyword"):
    """
    Classify the given text with respect to the target label (keyword or partype)

    Inputs:
        - text: a string with the given text that should be classified
        - label: if the classification should be w.r.t. the keyword or partype
    Returns:
        - pred_class: string with the predicted class
        - pred_score: classification score (percentage certainty)
        - htmlstr: html ready doc with words highlighted corresponding to the classifier decision
    """
    # load all the stuff we need for the classification
    vectorizer = joblib.load(f"src/assets/{label}_vectorizer.pkl")
    clf = joblib.load(f"src/assets/{label}_clf.pkl")
    # transform new text into features
    featmat_test = vectorizer.transform([text])
    # get class and score
    pred_class = clf.predict(featmat_test)[0]
    pred_score = 100 * clf.predict_proba(featmat_test)[0, clf.classes_ == pred_class][0]
    # transform the feature vector into a diagonal matrix
    feat_vec = lil_matrix((featmat_test.shape[1], featmat_test.shape[1]), dtype=float)
    feat_vec.setdiag(featmat_test[0, :].toarray().flatten())
    feat_vec = csr_matrix(feat_vec)
    # get the scores (i.e. before summing up)
    scores = clf.decision_function(feat_vec)
    # adapt for the intercept
    scores -= (1.0 - 1.0 / featmat_test.shape[1]) * clf.intercept_
    # binary or multi class?
    if len(scores.shape) == 1:
        if clf.classes_[0] == pred_class:
            # we want the scores which speak for the class - for the negative class,
            # the sign needs to be reversed
            scores *= -1.0
        scores_dict = dict(list(zip(vectorizer.get_feature_names_out(), scores, strict=True)))
    else:
        scores_dict = dict(
            list(zip(vectorizer.get_feature_names_out(), scores[:, clf.classes_ == pred_class][:, 0], strict=True))
        )
    # generate html
    htmlstr = scores2html(text, scores_dict, vectorizer.build_preprocessor())
    return pred_class.replace("_", " ").title(), pred_score, htmlstr


def train_clf(label="keyword"):
    """Train a classifier on the cancer papers dataset with the given target label (keyword or partype)"""
    from my_datasets.cancer_papers.load_cancer import articles2dict

    print("loading articles")
    textdict, doccats, _ = articles2dict(
        label=label,
        reduced_labels=False,
        combine_paragraphs=False,
        ignore_types=["Mixed"],
    )
    print("transforming articles into features")
    vectorizer = TfidfVectorizer(strip_accents="unicode")
    trainids = list(textdict.keys())
    featmat_train = vectorizer.fit_transform([textdict[tid] for tid in trainids])
    y_train = [doccats[tid] for tid in trainids]
    print("training classifier")
    clf = LogisticRegression(class_weight="balanced", random_state=1)
    clf.fit(featmat_train, y_train)
    # save all we need for later applying the clf to new docs
    joblib.dump(vectorizer, f"src/assets/{label}_vectorizer.pkl")
    joblib.dump(clf, f"src/assets/{label}_clf.pkl")


if __name__ == "__main__":
    for label in ["keyword", "partype"]:
        train_clf(label)
