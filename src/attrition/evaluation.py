from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix, brier_score_loss

def evaluate(y, probability, threshold=.5):
    pred = probability >= threshold
    return dict(accuracy=float(accuracy_score(y,pred)),precision=float(precision_score(y,pred,zero_division=0)),recall=float(recall_score(y,pred,zero_division=0)),f1=float(f1_score(y,pred,zero_division=0)),roc_auc=float(roc_auc_score(y,probability)),pr_auc=float(average_precision_score(y,probability)),brier_score=float(brier_score_loss(y,probability)),confusion_matrix=confusion_matrix(y,pred,labels=[0,1]).tolist())
