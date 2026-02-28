"""Template: evaluation metrics and plots"""

from sklearn.metrics import roc_auc_score, classification_report
import matplotlib.pyplot as plt


def evaluate(model, X_test, y_test):
    probs = model.predict_proba(X_test)[:,1]
    preds = model.predict(X_test)
    auc = roc_auc_score(y_test, probs)
    print('AUC', auc)
    print(classification_report(y_test, preds))
    return auc


def plot_roc_curve(fpr, tpr):
    plt.plot(fpr, tpr)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.show()
