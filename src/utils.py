import pickle
import re

import joblib
import matplotlib as mpl
import numpy as np
from matplotlib.cm import get_cmap
from nlputils.features import FeatureTransform, features2mat, preprocess_text
from scipy.sparse import csr_matrix, lil_matrix
from sklearn.linear_model import LogisticRegression


def scores2html(text, scores, highlight_oov=False):
    """
    Based on the original text and relevance scores, generate a html doc highlighting positive / negative words

    Inputs:
        - text: the raw text in which the words should be highlighted
        - scores: a dictionary with {word: score} or a list with tuples [(word, score)]
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
        scores = []
        for word in re.findall(r"[\w-]+", text, re.UNICODE):
            word_pp = preprocess_text(word, norm_num=False)
            if word_pp in scores_dict:
                scores.append((word, scores_dict[word_pp]))
            else:
                scores.append((word, None))
    else:
        N = np.max(np.abs([t[1] for t in scores if t[1] is not None]))
        scores = [(w, s / N) if s is not None else (w, None) for w, s in scores]

    htmlstr = '<div style="white-space: pre-wrap; font-family: monospace;">'
    resttext = text
    for word, score in scores:
        # was anything before the identified word? add it unchanged to the html
        htmlstr += resttext[: resttext.find(word)]
        # cut off the identified word
        resttext = resttext[resttext.find(word) + len(word) :]
        # get the colorcode of the word
        rgbac = (1.0, 1.0, 0.0)  # for unknown words
        alpha = 0.3 if highlight_oov else 0.0
        if score is not None:
            rgbac = cmap_neg(norm(-score)) if score < 0 else cmap_pos(norm(score))
            alpha = 0.5
        htmlstr += f'<span style="background-color: rgba({round(255 * rgbac[0])}, {round(255 * rgbac[1])}, {round(255 * rgbac[2])}, {alpha:.1f})">{word}</span>'
    # after the last word, add the rest of the text
    htmlstr += resttext
    htmlstr += "</div>"
    return htmlstr


def classify_me_why(text, label="keyword"):
    """
    classify the given text with respect to the target label (keyword or partype)

    Inputs:
        - text: a string with the given text that should be classified
        - label: if the classification should be w.r.t. the keyword or partype
    Returns:
        - pred_class: string with the predicted class
        - pred_score: classification score (percentage certainty)
        - htmlstr: html ready doc with words highlighted corresponding to the classifier decision
    """
    # load all the stuff we need for the classification
    with open(f"src/assets/{label}_ft.pkl", "rb") as f:
        ft = pickle.load(f)
    with open(f"src/assets/{label}_featurenames.pkl", "rb") as f:
        featurenames = pickle.load(f)
    clf = joblib.load(f"src/assets/{label}_clf.pkl")
    # transform new text into features
    textdict = {1: text}
    docfeats = ft.texts2features(textdict)
    featmat_test, _ = features2mat(docfeats, [1], featurenames)
    # get class and score
    pred_class = clf.predict(featmat_test)[0]
    pred_score = 100 * clf.predict_proba(featmat_test)[0, clf.classes_ == pred_class][0]
    # transform the feature vector into a diagonal matrix
    feat_vec = lil_matrix((len(featurenames), len(featurenames)), dtype=float)
    feat_vec.setdiag(featmat_test[0, :].toarray().flatten())
    feat_vec = csr_matrix(feat_vec)
    # get the scores (i.e. before summing up)
    scores = clf.decision_function(feat_vec)
    # adapt for the intercept
    scores -= (1.0 - 1.0 / len(featurenames)) * clf.intercept_
    # binary or multi class?
    if len(scores.shape) == 1:
        if clf.classes_[0] == pred_class:
            # we want the scores which speak for the class - for the negative class,
            # the sign needs to be reversed
            scores *= -1.0
        scores_dict = dict(list(zip(featurenames, scores)))
    else:
        scores_dict = dict(list(zip(featurenames, scores[:, clf.classes_ == pred_class][:, 0])))
    # generate html
    htmlstr = scores2html(text, scores_dict)
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
    trainids = list(textdict.keys())
    ft = FeatureTransform(norm="max", weight=True, renorm="max", identify_bigrams=False, norm_num=False)
    docfeats = ft.texts2features(textdict, fit_ids=trainids)
    featmat_train, featurenames = features2mat(docfeats, trainids)
    y_train = [doccats[tid] for tid in trainids]
    print("training classifier")
    clf = LogisticRegression(class_weight="balanced", random_state=1)
    clf.fit(featmat_train, y_train)
    # save all we need for later applying the clf to new docs
    with open(f"src/assets/{label}_ft.pkl", "wb") as f:
        pickle.dump(ft, f, -1)
    with open(f"src/assets/{label}_featurenames.pkl", "wb") as f:
        pickle.dump(featurenames, f, -1)
    joblib.dump(clf, f"src/assets/{label}_clf.pkl")


if __name__ == "__main__":
    for label in ["keyword", "partype"]:
        train_clf(label)
