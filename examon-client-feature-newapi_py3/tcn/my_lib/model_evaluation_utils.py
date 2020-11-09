from math import log10
import numpy as np

from sklearn.metrics import confusion_matrix

# Assign classes to predicted results, thresholding probabilites generated by "categorical_crossentropy" loss function
# Positive class assigned to values between lower threshold (lb_threshold) and upper threshold (ub_threshold)
def assign_class_rising_anomaly(rising_anomaly_predicted_probabilities, lb_threshold, ub_threshold) :
    predicted_class = np.zeros(shape=rising_anomaly_predicted_probabilities.shape)
    predicted_class[np.where((rising_anomaly_predicted_probabilities >= lb_threshold) & \
                   (rising_anomaly_predicted_probabilities <= ub_threshold))] = 1.0
    return predicted_class

# Compute a whole set of metrics (precision, recall, accuracy, f1_score)
def compute_metrics(tn, fp, fn, tp) :
    print("True Negative (TN): ", tn)
    print("False Positive (FP): ", fp)
    print("False Negative (FN): ", fn)
    print("True Positive (TP): ", tp)
    metrics = dict()
    metrics['accuracy'] = (tp+tn) / (tp+tn+fp+fn)
    metrics['precision'] = tp / (tp+fp)
    metrics['recall'] = tp / (tp+fn)
    if metrics['precision'] + metrics['recall'] != 0 :
        precision, recall = metrics['precision'], metrics['recall']
        metrics['f1_score'] = 2*(precision*recall) / (precision+recall)
    else :
        metrics['f1_score'] = -1
    print('--- METRICS ---')
    for key in metrics.keys() :
        print(key, ": ", metrics[key])
    return metrics


# Split threshold values between start and stop according to the choosen strategy.
# growth_mode could be 'same', 'increment_ub' or 'increment_lb':
    # 'same' means taking equal length intervals
    # 'increment_ub' means increment upper_bounds and fix lower_bound
    # 'increment_lb' means increment lower_bounds and fix upper_bound
# Strategy could be 'linear' or 'log' (base 10).

# I recommend to start from 'log' strategy with 'same' growth mode for a coarse grain analysis, and further use 'linear' with 'same', 'increment_lb' or 'increment_ub' for a fine grained analysis 
def get_thresholds_values(start, stop, num_steps, strategy='linear', growth_mode = 'same') :
    # Get thresholds
    if strategy == 'linear' :
        thresholds = np.linspace(start=start, stop=stop, num=num_steps+1)
    elif strategy == 'log' :
        thresholds = np.logspace(start=log10(start), stop=log10(stop), num=num_steps+1)
    
    lb_threshold_list = thresholds[:-1]
    ub_threshold_list = thresholds[1:]
     
    if growth_mode == 'increment_ub' :
        lb_threshold_list = np.repeat(start, num_steps)
    # If stop == 1 then fix <ub_threshold> to 1 for each iteration
    elif growth_mode == 'increment_lb' :
        ub_threshold_list = np.repeat(stop, num_steps)
    # IMPLICIT - else : iterate over fixed length intervals
    
    return lb_threshold_list, ub_threshold_list


# Compute best threshold for the given predictions (predicted_y) according to real class values (real_y), choosing between threshold bounds from 'start' to 'stop' computed according to the given strategy. 
def compute_best_threhsold(real_y, predicted_y, receptive_field, start, stop, num_steps, strategy='linear', growth_mode='same') :
    # Shift first <timeserie_receptive_field> useless values
    real_y_shifted = real_y.ravel()[receptive_field:]
    
    # Get threshold bounds
    lb_threshold_list, ub_threshold_list = get_thresholds_values(start, stop, num_steps, strategy, growth_mode)
    
    # Get best score's info
    info = get_best_score_info(lb_threshold_list, ub_threshold_list, predicted_y, real_y_shifted)
    
    return info


# Compute best score (according to the given metric). Lower bounds and upper bounds threshold values as probability bounds for the given predictions.
# Metrics could be 'accuracy', 'precision', 'recall' and 'f1_score'. Default is 'f1_score'
# NOTE: to add metrics. Refer to 'compute_metrics' function
def get_best_score_info(lb_thresholds, ub_thresholds, predicted_y, real_y, metric='f1_score') :
    # Default values to return
    info = { \
            'tn': -1, \
            'fp': -1, \
            'fn': -1, \
            'tp': -1, \
            'f1_score':-1, \
            'recall':-1, \
            'precision':-1, \
            'accuracy':-1, \
            'lb_threshold': -1, \
            'ub_threshold': -1 \
           }
    
    best_score = 0
    for lb, ub in zip(lb_thresholds, ub_thresholds) :
        
        print('.........................................................')
        print('current_LB_threshold: {:.2e}; current_UB_threshold: {:.2e}'.format(lb, ub))
        
        # Assign a class to the predictions
        predicted_rising_anomalies = assign_class_rising_anomaly(predicted_y, lb, ub)
        # Compute metric score
        tn, fp, fn, tp = confusion_matrix(real_y, predicted_rising_anomalies).ravel()
        current_scores = compute_metrics(tn, fp, fn, tp)

        if current_scores[metric] >= best_score :
            # Update best score
            best_score = current_scores[metric]
            info = { \
                    'tn': tn, \
                    'fp': fp, \
                    'fn': fn, \
                    'tp': tp, \
                    'accuracy': current_scores['accuracy'], \
                    'precision': current_scores['precision'], \
                    'recall': current_scores['recall'], \
                    'f1_score': current_scores['f1_score'], \
                    'lb_threshold': lb, \
                    'ub_threshold': ub \
                   }
            
    return info


# Print info returned by 'compute_best_threhsold'
def print_info(info) :
    print('--- BEST SCORE INFO ---')
    print('True Negative (TN): {}'.format(info['tn']))
    print('False Positive (FP): : {}'.format(info['fp']))
    print('False Negative (FN) {}'.format(info['fn']))
    print('True Positive (TP): {}'.format(info['tp']))
    print('accuracy: {:.4f}'.format(info['accuracy']))
    print('precision: {:.4f}'.format(info['precision']))
    print('recall: {:.4f}'.format(info['recall']))
    print('f1_score : {:.4f}'.format(info['f1_score']))
    print('LB Threshold {:.2e}'.format(info['lb_threshold']))
    print('UB Threshold: {:.2e}'.format(info['ub_threshold']))