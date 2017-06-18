import sql_persister
import numpy as np
from sklearn.cluster import MeanShift, KMeans

def get_features(persister):
    ids = [p['id'] for p in persister.get_person_ids()]
    persons_by_days = persister.get_persons_by_days()
    features = {}

    for person_by_day in persons_by_days:
        day_ = person_by_day['day']
        if day_:
            timestamp = day_.timestamp()
            if timestamp in features:
                feature_day = features[timestamp]
            else:
                feature_day = [timestamp] + [0] * len(ids)
                features[timestamp] = feature_day

            person_id = person_by_day['person_id']
            person_index = ids.index(person_id)
            feature_day[person_index + 1] = person_by_day['cnt']

    return list(features.values())


X = get_features(sql_persister.get())

clf = MeanShift()
clf.fit(np.array(X))

labels = clf.labels_
cluster_centers = clf.cluster_centers_

print(labels)
